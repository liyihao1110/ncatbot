import ast
import asyncio
import base64
import json
import os
import pickle
import warnings
import zipfile
from pathlib import Path
from typing import Any, Callable, Dict, Literal, Optional, Union

import httpx

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


def convert_uploadable_object(i, message_type):
    """将可上传对象转换为标准格式"""
    if i.startswith("http"):
        if message_type == "image":
            try:
                with httpx.Client() as client:
                    response = client.get(i)
                    response.raise_for_status()
                    image_data = response.content
                    i = f"base64://{base64.b64encode(image_data).decode('utf-8')}"
            except httpx.HTTPError as e:
                return {"type": "text", "data": {"text": f"URL请求失败: {e}"}}
            except Exception as e:
                return {"type": "text", "data": {"text": f"图片转换失败: {e}"}}
        return {"type": message_type, "data": {"file": i}}
    elif i.startswith("base64://"):
        return {"type": message_type, "data": {"file": i}}
    elif os.path.exists(i):
        if message_type == "image":
            with open(i, "rb") as f:
                image_data = f.read()
                i = f"base64://{base64.b64encode(image_data).decode('utf-8')}"
        else:
            i = f"file:///{os.path.abspath(i)}"
        return {"type": message_type, "data": {"file": i}}
    else:
        return {"type": message_type, "data": {"file": f"file:///{i}"}}


# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-13 21:47:01
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-04-04 17:35:35
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
    3. 创建UniversalLoader实例后不会立刻读取文件,请手动调用load或者aload读取文件

Raises:
    FileTypeUnknownError:       当文件类型无法识别时抛出
    FileNotFoundError:          当文件路径无效或文件不存在时抛出
    LoadError:                  当加载文件时发生错误时抛出
    SaveError:                  当保存文件时发生错误时抛出
    ModuleNotInstalledError:    当所需模块未安装时抛出
    ValueError:                 当手动开启pickle支持时抛出
"""


# ---------------------
# region 模块可用性检测区块
# ---------------------
# PICKLE
PICKLE_AVAILABLE = False  # 安全警告：需手动审核来源可信的pickle文件
# TODO 解决pickle异步加载的错误

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
    _open_file = aiofiles.open  # type: ignore
except ImportError:
    _open_file = open
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

JSON_TYPE = [bool, str, float, "None"]
YAML_TYPE = [bool, str, int, float, "None"]
TOML_TYPE = [str, float]
PICKLE_TYPE = [bool, str, "None"]

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
# region 主功能类实现
# ---------------------


class UniversalLoader(dict):
    _flag = "-"
    _custom_type_handlers = {}

    def __init__(self, file_path: Union[str, Path], file_type: Optional[str] = None):
        """
        初始化通用加载器

        :param file_path: 文件路径，支持字符串或Path对象
        :param file_type: 可选参数,手动指定文件类型（覆盖自动检测）
                        支持类型：json/toml/yaml/pickle

        示例：
            >>> loader = UniversalLoader("data.json")
            >>> loader.load()
        """
        super().__init__()
        self.file_path: Path = Path(file_path).resolve()  # 获取绝对路径
        self.file_type = file_type.lower() if file_type else self._detect_file_type()
        self._async_lock = asyncio.Lock()  # 异步操作锁

    def __enter__(self) -> "UniversalLoader":
        """上下文管理器入口: with instance as data"""
        return self.load()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """上下文管理器退出时自动保存"""
        if self:
            self.save()

    async def __aenter__(self) -> "UniversalLoader":
        """上下文管理器入口: with instance as data"""
        return await self.aload()

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """上下文管理器退出时自动保存"""
        if self:
            await self.asave()

    def _detect_file_type(self) -> str:
        """通过文件扩展名检测文件类型"""
        file_type_map = {
            "json": "json",
            "toml": "toml",
            "yaml": "yaml",
            "yml": "yaml",
            "pickle": "pickle",
        }
        ext = self.file_path.suffix.lower().lstrip(".")
        file_type = file_type_map.get(ext, None)
        if not file_type:
            raise FileTypeUnknownError(f"无法识别的文件格式: {self.file_path}")
        return file_type

    def _check_file_exists(self) -> None:
        """同步检查文件是否存在"""
        if not os.path.isfile(str(self.file_path)):
            raise FileNotFoundError(f"文件路径无效或不是文件: {self.file_path}")

    async def _async_check_file_exists(self) -> None:
        """异步检查文件存在性（通过线程池执行）"""
        await asyncio.to_thread(self._check_file_exists)

    # ---------------------
    # region 核心数据操作方法
    # ---------------------

    def load(self) -> "UniversalLoader":
        """
        同步加载数据

        :return: 自身实例，支持链式调用
        :raises LoadError: 加载过程中发生错误时抛出

        示例：
            >>> data = UniversalLoader("data.toml").load()
        """
        self._check_file_exists()
        try:
            self.update(self._load_data_sync())
        except Exception as e:
            raise LoadError(f"加载文件时出错: {e}") from e
        return self

    async def aload(self) -> "UniversalLoader":
        """
        异步加载数据（带锁保护）

        :return: 自身实例，支持链式调用
        :raises LoadError: 加载过程中发生错误时抛出
        """
        await self._async_check_file_exists()
        async with self._async_lock:
            try:
                self.update(await self._load_data_async())
            except Exception as e:
                raise LoadError(f"异步加载文件时出错: {e}") from e
        return self

    def save(self, save_path: Optional[Union[str, Path]] = None) -> "UniversalLoader":
        """
        同步保存数据到文件

        :param save_path: 可选保存路径，默认使用加载路径
        :return: 自身实例
        :raises SaveError: 保存过程中发生错误时抛出
        """
        save_path = Path(save_path).resolve() if save_path else self.file_path
        try:
            self._save_data_sync(save_path)
        except Exception as e:
            raise SaveError(f"保存文件时出错: {e}") from e
        return self

    async def asave(
        self, save_path: Optional[Union[str, Path]] = None
    ) -> "UniversalLoader":
        """
        异步保存数据到文件（带锁保护）

        :param save_path: 可选保存路径，默认使用加载路径
        :return: 自身实例
        :raises SaveError: 保存过程中发生错误时抛出
        """
        save_path = Path(save_path).resolve() if save_path else self.file_path
        await self._save_data_async(save_path)
        # async with self._async_lock:
        #     try:
        #         await self._save_data_async(save_path)
        #     except Exception as e:
        #         raise SaveError(f"异步保存文件时出错: {e}") from e
        # return self

    # endregion

    # ---------------------
    # region 类型转换相关方法
    # ---------------------

    @classmethod
    def register_type_handler(
        cls, type_name: str, serialize_func: Callable, deserialize_func: Callable
    ):
        """注册自定义类型的序列化与反序列化函数"""
        cls._custom_type_handlers[type_name] = (serialize_func, deserialize_func)

    def _type_convert(
        self,
        data: Any,
        mode: Literal["restore", "preserve"] = "preserve",
        exclude_types: list = [],
        encode_keys: bool = True,
        encode_values: bool = True,
    ) -> Any:
        """递归类型转换核心方法"""

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
        elif isinstance(data, (list, tuple)):
            converted = [
                self._type_convert(
                    item, mode, exclude_types, encode_keys, encode_values
                )
                for item in data
            ]
            rest = converted if isinstance(data, list) else tuple(converted)
            if mode == "preserve":
                if isinstance(data, tuple):
                    return f"{data.__class__.__name__}{self._flag}{rest}"
            return rest
        else:
            if mode == "preserve":
                if type(data) in exclude_types or str(data) in exclude_types:
                    return data  # 不标记在过滤器中的类型
                return self._preserve_item(data)
            else:
                return self._restore_item(data)

    def _preserve_item(self, item: Any) -> str:
        """将数据转换为类型标记字符串"""
        flag = self._flag

        if item is None:
            return f"NoneType{flag}None"

        type_name = item.__class__.__name__

        # 处理自定义类型
        if type_name in self._custom_type_handlers:
            serialize_func = self._custom_type_handlers[type_name][0]
            return f"{type_name}{flag}{serialize_func(item)}"

        # 处理基础类型
        if isinstance(item, (int, float, str, bool)):
            return f"{type_name}{flag}{item}"
        elif isinstance(item, type(None)):
            return f"NoneType{flag}None"

        # 处理容器类型
        elif isinstance(item, (list, tuple, dict)):
            if isinstance(item, list):
                preserved_list = [self._type_convert(i, "preserve") for i in item]
                return f"list{flag}{json.dumps(preserved_list)}"
            elif isinstance(item, tuple):
                preserved_tuple = [self._type_convert(i, "preserve") for i in item]
                return f"tuple{flag}{json.dumps(preserved_tuple)}"
            else:  # dict
                return self._type_convert(item, "preserve")

        # 其他类型保持原样
        return f"unknown{flag}{str(item)}"

    def _restore_item(self, item: Any) -> Any:
        """从类型标记字符串还原数据"""
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
        }
        if type_str in basic_types:
            try:
                if type_str == "bool":
                    return value_str.lower() == "true"
                elif type_str in ("list", "tuple"):
                    parsed = ast.literal_eval(value_str)
                    if type_str == "list":
                        return [self._restore_item(i) for i in parsed]
                    else:  # tuple
                        return tuple(self._restore_item(i) for i in parsed)
                elif type_str == "dict":
                    parsed = json.loads(value_str)
                    return {
                        self._restore_item(k): self._restore_item(v)
                        for k, v in parsed.items()
                    }
                else:
                    return basic_types[type_str](value_str)
            except (ValueError, json.JSONDecodeError):
                return item

        # 未知类型返回原始字符串
        return item

    # endregion

    # ---------------------
    # region 数据加载实现
    # ---------------------

    def _load_data_sync(self) -> Dict[str, Any]:
        """同步加载数据核心逻辑"""
        # JSON格式处理
        if self.file_type == "json":
            with self.file_path.open("r") as f:
                raw_data = ujson.load(f) if UJSON_AVAILABLE else json.load(f)
                return self._type_convert(raw_data, "restore")

        # TOML格式处理
        elif self.file_type == "toml":
            with self.file_path.open("r") as f:
                raw_data = toml.load(f)
                return self._type_convert(raw_data, "restore")

        # YAML格式处理
        elif self.file_type == "yaml":
            if not YAML_AVAILABLE:
                raise ModuleNotInstalledError("请安装 PyYAML 模块：pip install PyYAML")
            with self.file_path.open("r") as f:
                raw_data = yaml.safe_load(f) or {}
                return self._type_convert(raw_data, "restore")

        # Pickle格式处理
        elif self.file_type == "pickle":
            if not PICKLE_AVAILABLE:
                raise ValueError("请手动开启PICKLE支持")
            with self.file_path.open("rb") as f:
                raw_data = pickle.load(f)
                return self._type_convert(raw_data, "restore")

        else:
            raise FileTypeUnknownError(f"不支持的文件类型: {self.file_type}")

    async def _load_data_async(self) -> Dict[str, Any]:
        """异步加载数据核心逻辑"""
        if AIOFILES_AVAILABLE:
            async with aiofiles.open(self.file_path, "r") as f:
                content = await f.read()
                # JSON处理
                if self.file_type == "json":
                    return self._type_convert(
                        (
                            ujson.loads(content)
                            if UJSON_AVAILABLE
                            else json.loads(content)
                        ),
                        "restore",
                    )
                # TOML处理
                elif self.file_type == "toml":
                    return self._type_convert(toml.loads(content), "restore")

                # YAML处理
                elif self.file_type == "yaml":
                    return self._type_convert(yaml.safe_load(content) or {}, "restore")

                # pickle处理
                elif self.file_type == "pickle":
                    raise TypeError("pickle错误尚未解决")
                    # 'utf-8' codec can't decode byte 0x80 in position 0: invalid start byte

    # endregion

    # ---------------------
    # region 数据保存实现
    # ---------------------

    def _save_data_sync(self, save_path: Path) -> None:
        """同步保存数据核心逻辑"""

        # JSON格式保存
        if self.file_type == "json":
            converted_data = self._type_convert(self.copy(), "preserve", JSON_TYPE)
            # print(converted_data)
            with save_path.open("w") as f:
                if UJSON_AVAILABLE:
                    ujson.dump(converted_data, f, ensure_ascii=False, indent=4)
                else:
                    json.dump(converted_data, f, ensure_ascii=False, indent=4)

        # TOML格式保存
        elif self.file_type == "toml":
            converted_data = self._type_convert(self.copy(), "preserve", TOML_TYPE)
            with save_path.open("w") as f:
                toml.dump(converted_data, f)

        # YAML格式保存
        elif self.file_type == "yaml":
            converted_data = self._type_convert(self.copy(), "preserve", YAML_TYPE)
            with save_path.open("w") as f:
                yaml.dump(
                    converted_data, f, allow_unicode=True, default_flow_style=False
                )

        # Pickle格式保存
        elif self.file_type == "pickle":
            converted_data = self._type_convert(self.copy(), "preserve", PICKLE_TYPE)
            with save_path.open("wb") as f:
                pickle.dump(converted_data, f)

        else:
            raise FileTypeUnknownError(f"不支持的文件类型: {self.file_type}")

    async def _save_data_async(self, save_path: Path) -> None:
        """异步保存数据核心逻辑"""

        if AIOFILES_AVAILABLE:
            # JSON异步保存
            if self.file_type == "json":
                converted_data = self._type_convert(self.copy(), "preserve", JSON_TYPE)
                async with aiofiles.open(save_path, "w", encoding="utf-8") as f:
                    content = (
                        ujson.dumps(converted_data)
                        if UJSON_AVAILABLE
                        else json.dumps(converted_data)
                    )
                    return await f.write(content)

            # TOML异步保存
            elif self.file_type == "toml":
                converted_data = self._type_convert(self.copy(), "preserve", TOML_TYPE)
                async with aiofiles.open(save_path, "w") as f:
                    return await f.write(toml.dumps(converted_data))

            # YAML异步保存
            elif self.file_type == "yaml":
                converted_data = self._type_convert(self.copy(), "preserve", YAML_TYPE)
                async with aiofiles.open(save_path, "w") as f:
                    return await f.write(yaml.dump(converted_data, allow_unicode=True))
        # 其他格式回退同步保存
        return self._save_data_sync(save_path)


# endregion
