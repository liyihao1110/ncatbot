# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-13 21:47:01
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-06-24 20:50:37
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
    ValueError:                 当未手动开启pickle支持时抛出/不支持的解析方式
"""

import os
import ast
import json
import time
import pickle
import asyncio
import warnings
import functools
from pathlib import Path
from typing import Any, Callable, Dict, Literal, Optional, Union

# ---------------------
# region 常量
# ---------------------

start_time = time.perf_counter()
with open(__file__, 'r') as file:
    file_content = file.read()
end_time = time.perf_counter()
reading_time = end_time - start_time

# 文件操作防抖，根据读取自己的时间计算
FILE_DEBOUNCE_TIME = reading_time * 20

# regionend

# ---------------------
# region 模块可用性检测区块
# ---------------------

# watchdog检测
try:
    from watchdog.observers import Observer # type: ignore
    from watchdog.events import FileSystemEventHandler # type: ignore
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    warnings.warn("watchdog 模块未安装。实时读取功能将被禁用。", ImportWarning)

# PICKLE
PICKLE_AVAILABLE = True  # 安全警告：需手动审核来源可信的pickle文件

# TOML 模块检测
try:
    import toml  # type: ignore
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False  # 非关键依赖,静默处理

# 异步文件操作模块检测
try:
    import aiofiles  # type: ignore
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False
    warnings.warn("aiofiles 模块未安装。异步功能将被禁用。", ImportWarning)

# YAML 模块检测
try:
    import yaml  # type: ignore
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False  # 非关键依赖,静默处理

# 高性能JSON模块检测
try:
    import ujson  # type: ignore
    UJSON_AVAILABLE = True
except ImportError:
    UJSON_AVAILABLE = False  # 回退到标准json模块

# endregion

JSON_TYPE = [bool,str,float,'None']
YAML_TYPE = [bool,str,int,float,'None']
TOML_TYPE = [str,float]
PICKLE_TYPE = [bool,str,'None']

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
    class FileChangeHandler(FileSystemEventHandler): # type: ignore
        def __init__(self, callback: Callable, file_path: Path, on_modified_callbacks: list[Callable] = None):
            super().__init__()
            self.callback = callback
            self.file_path = file_path
            self.on_modified_callbacks = on_modified_callbacks or []
            self.last_modified = self._get_current_mtime()
        
        def _get_current_mtime(self):
            """获取当前文件修改时间"""
            try:
                return self.file_path.stat().st_mtime
            except OSError:
                return 0
        
        def on_modified(self, event):
            if event.is_directory or event.src_path != str(self.file_path):
                return
            
            current_mtime = self._get_current_mtime()
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
    _flag = '|'
    _custom_type_handlers = {}
    
    # 实时保存的触发方法列表
    _REALTIME_METHODS = [
        '__setitem__', '__delitem__', 'update', 
        'setdefault', 'pop', 'popitem', 'clear'
    ]
    
    def __init__(
        self,
        file_path: Union[str, Path],
        file_encoding: str = 'utf-8',
        realtime_save: bool = False,
        realtime_load: bool = False,
        file_type: Optional[str] = None,
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
        super().__init__()
        self._file_path: Path = Path(file_path).resolve()
        self.file_encoding: str = file_encoding
        self._file_type = file_type.lower() if file_type else self._detect_file_type()
        self._async_lock = asyncio.Lock()
        self._observer = None
        self._realtime_save = realtime_save
        self._on_modified_callbacks = []
        
        # 动态重写方法以实现实时保存
        if realtime_save:
            self._wrap_methods_for_realtime_save()
        
        self._setup_realtime_features(realtime_load)

    @property
    def file_path(self):
        return self._file_path

    @property
    def file_type(self):
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

    # 禁用
    # def backup(self, save_path: Path) -> None:
    #     """创建文件备份"""
    #     if save_path.exists():
    #         timestamp = time.strftime("%Y%m%d%H%M%S")
    #         backup_path = save_path.with_name(f"{save_path.stem}_{timestamp}{save_path.suffix}")
    #         try:
    #             shutil.copy(save_path, backup_path)
    #         except Exception as e:
    #             warnings.warn(f"自动备份失败: {e}")

    # 触发保存统一入口
    def _trigger_save(self) -> None:
        """触发保存操作"""
        if self._realtime_save:
            self.save()

    def add_change_callback(self, callback: Callable):
        """添加数据变更回调函数"""
        if not callable(callback):
            raise TypeError("回调必须是可调用对象")
        self._on_modified_callbacks.append(callback)

    def _setup_realtime_features(self, realtime_load: bool):
        """设置实时功能"""
        if realtime_load and WATCHDOG_AVAILABLE:
            self._observer = Observer()
            handler = FileChangeHandler(self.load, self._file_path, self._on_modified_callbacks)
            self._observer.schedule(handler, str(self._file_path.parent), recursive=False)
            self._observer.start()
        elif realtime_load:
            warnings.warn("实时读取功能不可用，缺少watchdog模块。", RuntimeWarning)

    def __del__(self):
        if getattr(self, '_observer', None):
            self._observer.stop()
            self._observer.join()

    def __enter__(self) -> 'UniversalLoader':
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._realtime_save:
            try:
                self.save()
            except SaveError as e:
                warnings.warn(f"自动保存失败: {e}")
    
    async def __aenter__(self) -> 'UniversalLoader':
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if self._realtime_save:
            try:
                await self.asave()
            except SaveError as e:
                warnings.warn(f"异步自动保存失败: {e}")

    def _detect_file_type(self) -> str:
        """通过文件扩展名检测文件类型"""
        file_type_map = {
            'json': 'json',
            'toml': 'toml',
            'yaml': 'yaml',
            'yml': 'yaml',
            'pickle': 'pickle'
        }
        ext = self._file_path.suffix.lower().lstrip('.')
        file_type = file_type_map.get(ext, None)
        if not file_type:
            raise FileTypeUnknownError(f"无法识别的文件格式: {self._file_path}")
        return file_type

    def _check_file_exists(self) -> None:
        if not os.path.isfile(str(self._file_path)):
            raise FileNotFoundError(f"文件路径无效或不是文件: {self._file_path}")

    async def _async_check_file_exists(self) -> None:
        await asyncio.to_thread(self._check_file_exists)

    # ---------------------
    # region 核心数据操作方法
    # ---------------------

    def load(self) -> 'UniversalLoader':
        self._check_file_exists()
        try:
            data = self._load_data_sync()
            self._validate_data_structure(data)
            self.clear()
            self.update(data)
        except Exception as e:
            raise LoadError(f"加载文件时出错: {e}") from e
        return self

    async def aload(self) -> 'UniversalLoader':
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

    def save(self, save_path: Optional[Union[str, Path]] = None) -> 'UniversalLoader':
        save_path = Path(save_path).resolve() if save_path else self._file_path
        try:
            self._save_data_sync(save_path)
        except Exception as e:
            raise SaveError(f"保存文件时出错: {e}") from e
        return self

    async def asave(self, save_path: Optional[Union[str, Path]] = None) -> 'UniversalLoader':
        save_path = Path(save_path).resolve() if save_path else self._file_path
        async with self._async_lock:
            try:
                await self._save_data_async(save_path)
            except Exception as e:
                raise SaveError(f"异步保存失败: {e}") from e
        return self

    def _validate_data_structure(self, data):
        if self._file_type == 'toml' and not isinstance(data, dict):
            raise ValueError("TOML格式只支持字典类型数据")
    # endregion

    # ---------------------
    # region 类型转换相关方法
    # ---------------------

    @classmethod
    def register_type_handler(cls, type_name: str, serialize_func: Callable, deserialize_func: Callable):
        cls._custom_type_handlers[type_name] = (serialize_func, deserialize_func)

    def _type_convert(
        self, 
        data: Any, 
        mode: Literal['restore', 'preserve'] = 'preserve', 
        exclude_types: list = [], 
        encode_keys: bool = True, 
        encode_values: bool = True
    ) -> Any:
        # 处理自定义类型
        if hasattr(data, '__class__') and data.__class__.__name__ in self._custom_type_handlers:
            if mode == 'preserve':
                return self._preserve_item(data)
            return self._restore_item(data)
        
        # 处理容器类型
        if isinstance(data, dict):
            return {
                (self._type_convert(k, mode, exclude_types, encode_keys, encode_values) if encode_keys else k):
                (self._type_convert(v, mode, exclude_types, encode_keys, encode_values) if encode_values else v)
                for k, v in data.items()
            }
        
        if isinstance(data, (list, tuple, set)):
            converted = [
                self._type_convert(item, mode, exclude_types, encode_keys, encode_values)
                for item in data
            ]
            return type(data)(converted)
        
        # 处理基本类型
        if mode == 'preserve':
            if type(data) in exclude_types or str(data) in exclude_types:
                return data
            return self._preserve_item(data)
        return self._restore_item(data)

    def _preserve_item(self, item: Any) -> str:
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
        elif isinstance(item, (list, tuple, dict, set)):
            container_type = type(item).__name__
            preserved = [self._type_convert(i, 'preserve') for i in item]
            return f"{container_type}{flag}{json.dumps(preserved)}"
                
        # 其他类型保持原样
        return f"unknown{flag}{str(item)}"

    def _restore_item(self, item: Any) -> Any:
        flag = self._flag

        if not isinstance(item, str) or flag not in item:
            return item
            
        type_str, value_str = item.split(flag, 1)
        
        # 处理特殊值
        if type_str == 'NoneType':
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
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'NoneType': type(None),
            'list': list,
            'tuple': tuple,
            'dict': dict,
            'set': set
        }
        if type_str in basic_types:
            try:
                if type_str == 'bool':
                    return value_str.lower() == 'true'
                elif type_str in ('list', 'tuple', 'set'):
                    parsed = ast.literal_eval(value_str)
                    restored = [self._restore_item(i) for i in parsed]
                    return basic_types[type_str](restored)
                elif type_str == 'dict':
                    parsed = json.loads(value_str)
                    return {self._restore_item(k): self._restore_item(v) for k, v in parsed.items()}
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
        if self._file_type == 'json':
            with self._file_path.open('r', encoding=self.file_encoding) as f:
                raw_data = ujson.load(f) if UJSON_AVAILABLE else json.load(f)
                return self._type_convert(raw_data, 'restore')
        
        elif self._file_type == 'toml':
            with self._file_path.open('r', encoding=self.file_encoding) as f:
                raw_data = toml.load(f)
                return self._type_convert(raw_data, 'restore')
        
        elif self._file_type == 'yaml':
            if not YAML_AVAILABLE:
                raise ModuleNotInstalledError("请安装 PyYAML 模块：pip install PyYAML")
            with self._file_path.open('r', encoding=self.file_encoding) as f:
                raw_data = yaml.safe_load(f) or {}
                return self._type_convert(raw_data, 'restore')
        
        elif self._file_type == 'pickle':
            if not PICKLE_AVAILABLE:
                raise ValueError("请手动开启PICKLE支持")
            with self._file_path.open('rb') as f:
                raw_data = pickle.load(f)
                return self._type_convert(raw_data, 'restore')
        
        else:
            raise FileTypeUnknownError(f"不支持的文件类型: {self._file_type}")

    async def _load_data_async(self) -> Dict[str, Any]:
        if AIOFILES_AVAILABLE:
            if self._file_type == 'json':
                async with aiofiles.open(self._file_path, 'r', encoding=self.file_encoding) as f:
                    content = await f.read()
                    return self._type_convert(ujson.loads(content) if UJSON_AVAILABLE else json.loads(content), 'restore')
            elif self._file_type == 'toml':
                async with aiofiles.open(self._file_path, 'r', encoding=self.file_encoding) as f:
                    content = await f.read()
                    return self._type_convert(toml.loads(content), 'restore')
            elif self._file_type == 'yaml':
                async with aiofiles.open(self._file_path, 'r', encoding=self.file_encoding) as f:
                    content = await f.read()
                    return self._type_convert(yaml.safe_load(content) or {}, 'restore')
            elif self._file_type == 'pickle':
                async with aiofiles.open(self._file_path, 'rb') as f:
                    content = await f.read()
                    raw_data = pickle.loads(content)
                    return self._type_convert(raw_data, 'restore')
        else:
            return self._load_data_sync()
    # endregion

    # ---------------------
    # region 数据保存实现
    # ---------------------
    def _save_data_sync(self, save_path: Path) -> None:
        if self._file_type == 'json':
            converted_data = self._type_convert(self.copy(), 'preserve', JSON_TYPE)
            with save_path.open('w', encoding=self.file_encoding) as f:
                if UJSON_AVAILABLE:
                    ujson.dump(converted_data, f, ensure_ascii=False, indent=4)
                else:
                    json.dump(converted_data, f, ensure_ascii=False, indent=4)
        
        elif self._file_type == 'toml':
            converted_data = self._type_convert(self.copy(), 'preserve', TOML_TYPE)
            with save_path.open('w', encoding=self.file_encoding) as f:
                toml.dump(converted_data, f)
        
        elif self._file_type == 'yaml':
            converted_data = self._type_convert(self.copy(), 'preserve', YAML_TYPE)
            with save_path.open('w', encoding=self.file_encoding) as f:
                yaml.dump(converted_data, f, allow_unicode=True, default_flow_style=False)
        
        elif self._file_type == 'pickle':
            converted_data = self._type_convert(self.copy(), 'preserve', PICKLE_TYPE)
            with save_path.open('wb') as f:
                pickle.dump(converted_data, f)
        
        else:
            raise FileTypeUnknownError(f"不支持的文件类型: {self._file_type}")

    async def _save_data_async(self, save_path: Path) -> None:
        if AIOFILES_AVAILABLE:
            if self._file_type == 'json':
                converted_data = self._type_convert(self.copy(), 'preserve', JSON_TYPE)
                async with aiofiles.open(save_path, 'w', encoding=self.file_encoding) as f:
                    content = ujson.dumps(converted_data) if UJSON_AVAILABLE else json.dumps(converted_data)
                    await f.write(content)
            elif self._file_type == 'toml':
                converted_data = self._type_convert(self.copy(), 'preserve', TOML_TYPE)
                async with aiofiles.open(save_path, 'w', encoding=self.file_encoding) as f:
                    await f.write(toml.dumps(converted_data))
            elif self._file_type == 'yaml':
                converted_data = self._type_convert(self.copy(), 'preserve', YAML_TYPE)
                async with aiofiles.open(save_path, 'w', encoding=self.file_encoding) as f:
                    await f.write(yaml.dump(converted_data, allow_unicode=True))
            elif self._file_type == 'pickle':
                converted_data = self._type_convert(self.copy(), 'preserve', PICKLE_TYPE)
                async with aiofiles.open(save_path, 'wb') as f:
                    await f.write(pickle.dumps(converted_data))
        else:
            self._save_data_sync(save_path)
# endregion

# ---------------------
# region 额外数据类型支持
# ---------------------

# UUID支持
from uuid import UUID
def uuid_serialize(uuid_obj):
    return str(uuid_obj)

def uuid_deserialize(uuid_str):
    return UUID(uuid_str)

UniversalLoader.register_type_handler('UUID', uuid_serialize, uuid_deserialize)

# datetime支持
from datetime import datetime
def datetime_serialize(dt):
    return dt.isoformat()

def datetime_deserialize(dt_str):
    return datetime.fromisoformat(dt_str)

UniversalLoader.register_type_handler('datetime', datetime_serialize, datetime_deserialize)

# Decimal支持
from decimal import Decimal
def decimal_serialize(dec):
    return str(dec)

def decimal_deserialize(dec_str):
    return Decimal(dec_str)

UniversalLoader.register_type_handler('Decimal', decimal_serialize, decimal_deserialize)
# endregion