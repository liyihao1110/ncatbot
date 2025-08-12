import ast
import asyncio
import base64
import json
import os
import pickle
import re
import urllib
import warnings
import zipfile
from pathlib import Path
from typing import Any, Callable, Dict, Literal, Optional, Union
from urllib.parse import urljoin  # 导入urljoin函数

from ncatbot.utils.logger import get_log

_log = get_log()


def unzip_file(file_name, exact_path, remove=False):
    try:
        with zipfile.ZipFile(file_name, "r") as zip_ref:
            zip_ref.extractall(exact_path)
            _log.info(f"解压 {file_name} 成功")
        if remove:
            os.remove(file_name)
    except Exception:
        _log.error(f"解压 {file_name} 失败")
        return


def read_file(file_path) -> any:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def convert_uploadable_object(i, message_type, use_b64=False):
    """将可上传对象转换为标准格式"""

    def is_base64(s: str):
        if s.startswith("base64://"):
            return True
        if re.match(
            r"data:image/(jpg|jpeg|png|gif|bmp|webp|tiff|svg|mp4|avi|mov|wmv|flv|mkv|mpg|mpeg|m4v);base64,",
            s,
        ):
            return True
        return False

    def to_base64(s: str):
        if s.startswith("base64://"):
            return s
        if re.match(
            r"data:image/(jpg|jpeg|png|gif|bmp|webp|tiff|svg|mp4|avi|mov|wmv|flv|mkv|mpg|mpeg|m4v);base64,",
            s,
        ):
            m = re.match(
                r"data:image/(jpg|jpeg|png|gif|bmp|webp|tiff|svg|mp4|avi|mov|wmv|flv|mkv|mpg|mpeg|m4v);base64,(.*)",
                s,
            )
            return f"base64://{m.group(2)}"

    if i.startswith("http"):
        return {"type": message_type, "data": {"file": i}}
    elif is_base64(i):
        return {"type": message_type, "data": {"file": to_base64(i)}}
    elif os.path.exists(i):
        if not use_b64:
            return {"type": message_type, "data": {"file": os.path.abspath(i)}}
        elif message_type == "image":
            with open(i, "rb") as f:
                image_data = f.read()
                i = f"base64://{base64.b64encode(image_data).decode('utf-8')}"
        else:
            i = urljoin(
                "file:",
                f"base64://{base64.b64encode(open(i, 'rb').read()).decode('utf-8')}",
            )
        return {"type": message_type, "data": {"file": i}}
    else:
        # 文件不存在时同样规范处理(可能在 NapCat 机子上)
        file_url = urljoin("file:", urllib.request.pathname2url(os.path.abspath(i)))
        return {"type": message_type, "data": {"file": file_url}}


# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-13 21:47:01
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-07-08 13:09:51
# @Description  : 通用文件加载器，支持JSON/TOML/YAML/PICKLE格式的同步/异步读写
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
"""
通用文件加载器

支持格式: JSON/TOML/YAML(/PICKLE[需手动开启])
支持同步/异步操作,自动检测文件类型,异步锁保护异步操作
注意:
    1. UniversalLoader 并不是一个专门用于处理纯列表的工具
    2. 读取未知来源的pickle文件可能导致任意代码执行漏洞请手动开启支持
    3. 创建UniversalLoader实例后会立刻读取文件

Raises:
    FileTypeUnknownError:       当文件类型无法识别时抛出
    FileNotFoundError:          当文件路径无效或文件不存在时抛出
    LoadError:                  当加载文件时发生错误时抛出
    SaveError:                  当保存文件时发生错误时抛出
    ModuleNotInstalledError:    当所需模块未安装时抛出
    ValueError:                 当未手动开启pickle支持时抛出/不支持的解析方式
"""

import functools

# ---------------------
# region 常量
# ---------------------

# 文件操作防抖时间(100ms)
# ! 此值过高只会造成读取延迟，但是过低会导致频繁触发保存操作
# ! 需要根据实际情况调整
FILE_DEBOUNCE_TIME = 0.1

# regionend

# ---------------------
# region 模块可用性检测区块
# ---------------------

# watchdog检测
WATCHDOG_AVAILABLE = False
try:
    from watchdog.events import FileSystemEventHandler  # type: ignore
    from watchdog.observers import Observer  # type: ignore

    WATCHDOG_AVAILABLE = True
except ImportError:
    warnings.warn("watchdog 模块未安装。实时读取功能将被禁用。", ImportWarning)

# PICKLE
PICKLE_AVAILABLE = False  # ! 安全警告：需手动审核来源可信的pickle文件

# TOML 模块检测
TOML_AVAILABLE = False
try:
    import toml  # type: ignore

    TOML_AVAILABLE = True
except ImportError:
    pass  # 非关键依赖,静默处理

# 异步文件操作模块检测
AIOFILES_AVAILABLE = False
try:
    import aiofiles  # type: ignore

    AIOFILES_AVAILABLE = True
except ImportError:
    warnings.warn("aiofiles 模块未安装。异步功能将被禁用。", ImportWarning)

# YAML 模块检测
YAML_AVAILABLE = False
try:
    import yaml  # type: ignore

    YAML_AVAILABLE = True
except ImportError:
    pass  # 非关键依赖,静默处理

# 高性能JSON模块检测
UJSON_AVAILABLE = False
try:
    import ujson  # type: ignore

    UJSON_AVAILABLE = True
except ImportError:
    pass  # 回退到标准json模块

# endregion

# 格式支持类型
JSON_TYPE = [bool, str, float, "None"]
YAML_TYPE = [bool, str, int, float, "None"]
TOML_TYPE = [str, float]  # 不清楚
PICKLE_TYPE = [bool, str, "None"]  # 不清楚

# ---------------------
# region 异常类定义区块
# ---------------------


class UniversalLoaderError(Exception):
    """通用加载器错误基类"""

    pass


class LoadError(UniversalLoaderError):
    """数据加载错误"""

    pass


class SaveError(UniversalLoaderError):
    """数据保存错误"""

    pass


class FileTypeUnknownError(UniversalLoaderError):
    """文件类型未知错误"""

    pass


class ModuleNotInstalledError(UniversalLoaderError):
    """所需模块未安装错误"""

    pass


# endregion

# ---------------------
# region 文件修改检测与回调
# ---------------------
if WATCHDOG_AVAILABLE:

    class FileChangeHandler(FileSystemEventHandler):
        """处理文件变更事件的类"""

        def __init__(
            self,
            callback: Callable,
            file_path: Path,
            on_modified_callbacks: list[Callable] = None,
        ):
            super().__init__()
            self.callback = callback
            self.file_path = file_path
            self.on_modified_callbacks = on_modified_callbacks or []
            self.last_modified = self._get_current_mtime(self.file_path)

        @staticmethod
        def _get_current_mtime(file_path: Path) -> float:
            """获取当前文件修改时间"""
            try:
                return file_path.stat().st_mtime
            except OSError:
                return 0

        def on_modified(self, event):
            """文件修改事件处理"""
            if event.is_directory or event.src_path != str(self.file_path):
                return

            current_mtime = self._get_current_mtime(self.file_path)
            if current_mtime > self.last_modified + FILE_DEBOUNCE_TIME:  # 防抖
                self.last_modified = current_mtime
                self.callback()
                for cb in self.on_modified_callbacks:
                    try:
                        cb()
                    except Exception as e:
                        warnings.warn(f"执行文件修改回调时出错: {e}")


# endregion


# ---------------------
# region 主功能类实现
# ---------------------
class UniversalLoader(dict):
    """
    通用加载器，支持多种文件类型的数据加载与保存。

    该加载器可以根据文件扩展名自动识别文件类型，提供实时保存和实时读取功能。
    实时保存功能会在数据变更时自动保存到文件，实时读取功能会在文件变更时自动重新加载数据。

    Attributes:
        realtime_save (bool): 是否启用实时保存（数据变更时自动保存）。
        realtime_load (bool): 是否启用实时读取（文件变更时自动重新加载）。
        file_path (str, Path): 文件路径。
        file_type (str): 手动指定文件类型（覆盖自动检测）。
    """

    _flag = "|"
    _custom_type_handlers = {}

    # 实时保存的触发方法列表
    _REALTIME_METHODS = {
        "__setitem__",
        "__delitem__",
        "update",
        "setdefault",
        "pop",
        "popitem",
        "clear",
    }

    # 文件类型映射
    FILE_TYPE_MAP = {
        "json": "json",
        "toml": "toml",
        "yaml": "yaml",
        "yml": "yaml",
        "pickle": "pickle",
    }

    # 文件模式映射
    _FILE_MODES = {"json": "text", "toml": "text", "yaml": "text", "pickle": "binary"}

    # 同步加载器映射
    _SYNC_LOADERS = {
        "json": lambda self, f: ujson.load(f) if UJSON_AVAILABLE else json.load(f),
        "toml": lambda self, f: toml.load(f),
        "yaml": lambda self, f: yaml.safe_load(f) or {},
        "pickle": lambda self, f: pickle.load(f),
    }

    # 同步保存器映射
    _SYNC_SAVERS = {
        "json": lambda self, data, f: (
            ujson.dump(data, f, ensure_ascii=False, indent=4)
            if UJSON_AVAILABLE
            else json.dump(data, f, ensure_ascii=False, indent=4)
        ),
        "toml": lambda self, data, f: toml.dump(data, f),
        "yaml": lambda self, data, f: yaml.dump(
            data, f, allow_unicode=True, default_flow_style=False
        ),
        "pickle": lambda self, data, f: pickle.dump(data, f),
    }

    # 异步加载器映射
    _ASYNC_LOADERS = {
        "json": lambda self, content: (
            ujson.loads(content) if UJSON_AVAILABLE else json.loads(content)
        ),
        "toml": lambda self, content: toml.loads(content),
        "yaml": lambda self, content: yaml.safe_load(content) or {},
        "pickle": lambda self, content: pickle.loads(content),
    }

    # 异步保存器映射
    _ASYNC_SAVERS = {
        "json": lambda self, data: (
            ujson.dumps(data, ensure_ascii=False, indent=4)
            if UJSON_AVAILABLE
            else json.dumps(data, ensure_ascii=False, indent=4)
        ),
        "toml": lambda self, data: toml.dumps(data),
        "yaml": lambda self, data: yaml.dump(data, allow_unicode=True),
        "pickle": lambda self, data: pickle.dumps(data),
    }

    def __init__(
        self,
        file_path: Union[str, Path],
        file_encoding: str = "utf-8",
        realtime_save: bool = False,
        realtime_load: bool = False,
        file_type: Optional[str] = None,
        default: dict = {},
    ):
        """
        初始化通用加载器。

        Args:
            file_path: 文件路径，支持字符串或Path对象
            file_encoding: 文件编码
            realtime_save: 是否启用实时保存
            realtime_load: 是否启用实时读取
            file_type: 手动指定文件类型
        """
        super().__init__(default)
        self._file_path: Path = Path(file_path).resolve()
        self._file_encoding: str = file_encoding
        self._file_type = (
            file_type.lower() if file_type else self._detect_file_type(self._file_path)
        )
        self._async_lock = asyncio.Lock()
        self._observer = None
        self._realtime_save = realtime_save
        self._on_modified_callbacks = []
        # 检查模块可用性
        self._check_module_availability()

        self.load()  # 初始化时加载数据
        # 动态重写方法以支持实时保存
        if realtime_save:
            self._wrap_methods_for_realtime_save()

        self._setup_realtime_features(realtime_load)

    def _check_module_availability(self):
        """检查所需模块是否可用"""
        if self._file_type == "yaml" and not YAML_AVAILABLE:
            raise ModuleNotInstalledError("请安装 PyYAML 模块：pip install PyYAML")
        if self._file_type == "pickle" and not PICKLE_AVAILABLE:
            raise ValueError("请手动开启PICKLE支持")
        if self._file_type == "toml" and not TOML_AVAILABLE:
            raise ModuleNotInstalledError("请安装 toml 模块：pip install toml")

    @property
    def file_path(self) -> Path:
        """文件路径"""
        return self._file_path

    @property
    def file_type(self) -> str:
        """文件类型"""
        return self._file_type

    @property
    def file_encoding(self) -> str:
        """文件编码"""
        return self._file_type

    def _wrap_methods_for_realtime_save(self):
        """动态重写字典方法以实现实时保存功能"""
        for method_name in self._REALTIME_METHODS:
            original_method = getattr(super(), method_name)

            @functools.wraps(original_method)
            def wrapper(*args, __method=original_method, **kwargs):
                result = __method(*args, **kwargs)
                self._trigger_save()
                return result

            setattr(self, method_name, wrapper)

    # 触发保存统一入口
    def _trigger_save(self) -> None:
        """触发保存操作"""
        if self._realtime_save:
            self.save()

    def add_change_callback(self, callback: Callable):  # 也许应该改成内部的
        """添加数据变更回调函数"""
        if not WATCHDOG_AVAILABLE:
            raise ModuleNotInstalledError("实时读取功能不可用，缺少watchdog模块")
        if not callable(callback):
            raise TypeError("回调必须是可调用对象")
        self._on_modified_callbacks.append(callback)

    def _setup_realtime_features(self, realtime_load: bool):
        """设置实时功能"""
        if realtime_load and WATCHDOG_AVAILABLE:
            self._observer = Observer()
            handler = FileChangeHandler(
                self.load, self._file_path, self._on_modified_callbacks
            )
            self._observer.schedule(
                handler, str(self._file_path.parent), recursive=False
            )
            self._observer.start()
        elif realtime_load:
            warnings.warn(
                "实时读取功能不可用，缺少watchdog模块。", ModuleNotInstalledError
            )

    def __del__(self):
        if getattr(self, "_observer", None):
            self._observer.stop()
            self._observer.join()

    def __enter__(self) -> "UniversalLoader":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._realtime_save:
            try:
                if self._file_path and self._check_file_exists(self._file_path):
                    self.save()
            except SaveError as e:
                warnings.warn(f"自动保存失败: {e}")

    async def __aenter__(self) -> "UniversalLoader":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if self._realtime_save:
            try:
                if self._file_path and self._check_file_exists(self._file_path):
                    await self.asave()
            except SaveError as e:
                warnings.warn(f"异步自动保存失败: {e}")

    @classmethod
    def _detect_file_type(cls, path: Path) -> str:
        """通过文件扩展名检测文件类型"""
        ext = path.suffix.lower().lstrip(".")
        file_type = cls.FILE_TYPE_MAP.get(ext, None)
        if not file_type:
            raise FileTypeUnknownError(f"无法识别的文件格式: {path}")
        return file_type

    @staticmethod
    def _check_file_exists(path: Path) -> None:
        """文件检查逻辑"""
        if not path.exists():
            # 创建父目录
            path.parent.mkdir(parents=True, exist_ok=True)
            # 创建空文件
            path.touch()
            with open(path, "w", encoding="utf-8") as f:
                f.write(
                    """{
    "config": {}
}"""
                )
        elif not path.is_file():
            raise FileNotFoundError(f"路径不是文件: {path}")

    async def _async_check_file_exists(self) -> None:
        """异步检查文件是否存在"""
        await asyncio.to_thread(self._check_file_exists, self._file_path)

    # ---------------------
    # region 核心数据操作方法
    # ---------------------

    def load(self) -> "UniversalLoader":
        """同步加载文件数据"""
        self._check_file_exists(self._file_path)
        try:
            data = self._load_data_sync()
            self._validate_data_structure(data)
            self.clear()
            self.update(data)
        except Exception as e:
            raise LoadError(f"加载文件时出错: {e}") from e
        return self

    async def aload(self) -> "UniversalLoader":
        """异步加载文件数据"""
        await self._async_check_file_exists()
        async with self._async_lock:
            try:
                data = await self._load_data_async()
                self._validate_data_structure(data)
                self.clear()
                self.update(data)
            except Exception as e:
                raise LoadError(f"异步加载文件时出错: {e}") from e
        return self

    def save(self, save_path: Optional[Union[str, Path]] = None) -> "UniversalLoader":
        """同步保存数据到文件"""
        save_path = Path(save_path).resolve() if save_path else self._file_path
        try:
            # 确保目录存在
            save_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_data_sync(save_path)
        except Exception as e:
            raise SaveError(f"保存失败: {e}") from e
        return self

    async def asave(
        self, save_path: Optional[Union[str, Path]] = None
    ) -> "UniversalLoader":
        """异步保存数据到文件"""
        save_path = Path(save_path).resolve() if save_path else self._file_path
        async with self._async_lock:
            try:
                await self._save_data_async(save_path)
            except Exception as e:
                raise SaveError(f"异步保存失败: {e}") from e
        return self

    def _validate_data_structure(self, data: Any):
        """验证数据结构"""
        if self._file_type == "toml" and not isinstance(data, dict):
            raise ValueError("TOML格式只支持字典类型数据")

    # endregion

    # ---------------------
    # region 类型转换相关方法
    # ---------------------

    @classmethod
    def register_type_handler(
        cls, type_name: str, serialize_func: Callable, deserialize_func: Callable
    ):
        """注册自定义类型处理器"""
        cls._custom_type_handlers[type_name] = (serialize_func, deserialize_func)

    def _type_convert(
        self,
        data: Any,
        mode: Literal["restore", "preserve"] = "preserve",
        exclude_types: list = [],
        encode_keys: bool = True,
        encode_values: bool = True,
    ) -> Any:
        """类型转换主方法"""
        # 处理容器类型
        if isinstance(data, dict):
            return {
                (
                    self._type_convert(
                        k, mode, exclude_types, encode_keys, encode_values
                    )
                    if encode_keys
                    else k
                ): (
                    self._type_convert(
                        v, mode, exclude_types, encode_keys, encode_values
                    )
                    if encode_values
                    else v
                )
                for k, v in data.items()
            }

        if isinstance(data, (list, tuple, set)):
            converted = [
                self._type_convert(
                    item, mode, exclude_types, encode_keys, encode_values
                )
                for item in data
            ]
            return type(data)(converted)

        # 处理基本类型
        if mode == "preserve":
            if type(data) in exclude_types or str(data) in exclude_types:
                return data
            return self._preserve_item(data)
        return self._restore_item(data)

    def _preserve_item(self, item: Any) -> str:
        """保留类型的信息转换"""
        if item is None:
            return f"NoneType{self._flag}None"

        item_type = type(item)
        type_name = item_type.__name__

        # 处理基础类型
        if item_type in (int, float, str, bool):
            return f"{type_name}{self._flag}{item}"

        # 处理自定义类型
        if type_name in self._custom_type_handlers:
            serialize_func = self._custom_type_handlers[type_name][0]
            return f"{type_name}{self._flag}{serialize_func(item)}"

        # 其他类型转为字符串
        return f"unknown{self._flag}{str(item)}"

    def _restore_item(self, item: Any) -> Any:
        """恢复原始类型转换"""
        flag = self._flag

        if not isinstance(item, str) or flag not in item:
            return item

        type_str, value_str = item.split(flag, 1)

        # 处理特殊值
        if type_str == "NoneType":
            return None

        # 处理自定义类型
        if type_str in self._custom_type_handlers:
            try:
                deserialize_func = self._custom_type_handlers[type_str][1]
                return deserialize_func(value_str)
            except Exception:
                return item

        # 处理基础类型
        basic_types = {
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "NoneType": type(None),
            "list": list,
            "tuple": tuple,
            "dict": dict,
            "set": set,
        }
        if type_str in basic_types:
            try:
                if type_str == "bool":
                    return value_str.lower() == "true"
                elif type_str in ("list", "tuple", "set"):
                    parsed = ast.literal_eval(value_str)
                    restored = [self._restore_item(i) for i in parsed]
                    return basic_types[type_str](restored)
                elif type_str == "dict":
                    parsed = json.loads(value_str)
                    return {
                        self._restore_item(k): self._restore_item(v)
                        for k, v in parsed.items()
                    }
                else:
                    return basic_types[type_str](value_str)
            except (ValueError, json.JSONDecodeError, SyntaxError):
                return item

        return item

    # endregion

    # ---------------------
    # region 数据加载实现
    # ---------------------

    def _load_data_sync(self) -> Dict[str, Any]:
        """同步加载数据实现"""
        file_mode = self._FILE_MODES[self._file_type]
        loader = self._SYNC_LOADERS.get(self._file_type)

        if not loader:
            raise FileTypeUnknownError(f"不支持的文件类型: {self._file_type}")

        try:
            if file_mode == "text":
                try:
                    with self._file_path.open("r", encoding=self._file_encoding) as f:
                        raw_data = loader(self, f)
                except UnicodeDecodeError:
                    with self._file_path.open("r", encoding="gbk") as f:
                        raw_data = loader(self, f)
            else:  # b
                with self._file_path.open("rb") as f:
                    raw_data = loader(self, f)

            return self._type_convert(raw_data, "restore")
        except Exception as e:
            raise LoadError(f"加载文件时出错: {e}") from e

    async def _load_data_async(self) -> Dict[str, Any]:
        """异步加载数据实现"""
        file_mode = self._FILE_MODES[self._file_type]
        loader = self._ASYNC_LOADERS.get(self._file_type)

        if not loader:
            raise FileTypeUnknownError(f"不支持的文件类型: {self._file_type}")

        try:
            if AIOFILES_AVAILABLE:
                if file_mode == "text":
                    try:
                        async with aiofiles.open(
                            self._file_path, "r", encoding=self._file_encoding
                        ) as f:
                            content = await f.read()
                    except UnicodeDecodeError:
                        async with aiofiles.open(
                            self._file_path, "r", encoding="gbk"
                        ) as f:
                            content = await f.read()
                else:  # b
                    async with aiofiles.open(self._file_path, "rb") as f:
                        content = await f.read()

                raw_data = loader(self, content)
                return self._type_convert(raw_data, "restore")
            else:
                return self._load_data_sync()
        except Exception as e:
            raise LoadError(f"异步加载文件时出错: {e}") from e

    # endregion

    # ---------------------
    # region 数据保存实现
    # ---------------------
    def _save_data_sync(self, save_path: Path) -> None:
        """同步保存数据实现"""
        file_mode = self._FILE_MODES[self._file_type]
        saver = self._SYNC_SAVERS.get(self._file_type)

        if not saver:
            raise FileTypeUnknownError(f"不支持的文件类型: {self._file_type}")

        converted_data = self._type_convert(
            self.copy(), "preserve", self._get_exclude_types()
        )

        try:
            if file_mode == "text":
                with save_path.open("w", encoding=self._file_encoding) as f:
                    saver(self, converted_data, f)
            else:  # b
                with save_path.open("wb") as f:
                    saver(self, converted_data, f)
        except Exception as e:
            raise SaveError(f"保存文件时出错: {e}") from e

    async def _save_data_async(self, save_path: Path) -> None:
        """异步保存数据实现"""
        file_mode = self._FILE_MODES[self._file_type]
        saver = self._ASYNC_SAVERS.get(self._file_type)

        if not saver:
            raise FileTypeUnknownError(f"不支持的文件类型: {self._file_type}")

        converted_data = self._type_convert(
            self.copy(), "preserve", self._get_exclude_types()
        )

        try:
            if AIOFILES_AVAILABLE:
                serialized_data = saver(self, converted_data)

                if file_mode == "text":
                    async with aiofiles.open(
                        save_path, "w", encoding=self._file_encoding
                    ) as f:
                        await f.write(serialized_data)
                else:  # b
                    async with aiofiles.open(save_path, "wb") as f:
                        await f.write(serialized_data)
            else:
                self._save_data_sync(save_path)
        except Exception as e:
            raise SaveError(f"异步保存失败: {e}") from e

    def _get_exclude_types(self) -> list:
        """获取当前文件类型对应的排除类型"""
        type_map = {
            "json": JSON_TYPE,
            "toml": TOML_TYPE,
            "yaml": YAML_TYPE,
            "pickle": PICKLE_TYPE,
        }
        return type_map.get(self._file_type, [])


# endregion

# ---------------------
# region 额外数据类型支持
# ---------------------

# UUID支持
from uuid import UUID


def uuid_serialize(uuid_obj: UUID):
    return str(uuid_obj)


def uuid_deserialize(uuid_str):
    return UUID(uuid_str)


UniversalLoader.register_type_handler("UUID", uuid_serialize, uuid_deserialize)

# datetime支持
from datetime import datetime


def datetime_serialize(dt: datetime):
    return dt.isoformat()


def datetime_deserialize(dt_str):
    return datetime.fromisoformat(dt_str)


UniversalLoader.register_type_handler(
    "datetime", datetime_serialize, datetime_deserialize
)

# Decimal支持
from decimal import Decimal


def decimal_serialize(dec: Decimal):
    return str(dec)


def decimal_deserialize(dec_str):
    return Decimal(dec_str)


UniversalLoader.register_type_handler("Decimal", decimal_serialize, decimal_deserialize)
# endregion
