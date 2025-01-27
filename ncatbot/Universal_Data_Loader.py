import asyncio
import json
import os
import warnings
import xml.etree.ElementTree as ET
from configparser import ConfigParser
from typing import Dict, Any, Optional

# 检测模块可用性
TOML_AVAILABLE = False
AIOFILES_AVAILABLE = False
YAML_AVAILABLE = False
PICKLE_AVAILABLE = False
UJSON_AVAILABLE = False

try:
    import toml # type: ignore
    TOML_AVAILABLE = True
except ImportError:
    warnings.warn("toml 模块未安装。相关功能将被禁用。", ImportWarning)

try:
    import aiofiles # type: ignore
    AIOFILES_AVAILABLE = True
    _open_file = aiofiles.open
except ImportError:
    _open_file = open
    warnings.warn("aiofiles 模块未安装。异步功能将被禁用。", ImportWarning)

try:
    import yaml # type: ignore
    YAML_AVAILABLE = True
except ImportError:
    pass

# try:
#     import pickle # type: ignore
#     PICKLE_AVAILABLE = True
#     warnings.warn("Pickle 加载数据存在安全风险！如果您加载了不受信任的数据，可能会导致任意代码执行攻击！", UserWarning)
# except ImportError:
#     pass

try:
    import ujson # type: ignore
    UJSON_AVAILABLE = True
except ImportError:
    pass


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


class UniversalLoader:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.data: Dict[str, Any] = {}
        self.file_type = self._detect_file_type()

    def _detect_file_type(self) -> Optional[str]:
        """检测文件类型"""
        file_type_map = {
            'json': 'json',
            'toml': 'toml',
            'yaml': 'yaml',
            'yml': 'yaml',
            'ini': 'ini',
            'xml': 'xml',
            'properties': 'properties',
            'pickle': 'pickle'
        }
        ext = self.file_path.lower().rsplit('.', 1)[-1] if '.' in self.file_path else ''
        file_type = file_type_map.get(ext, None)
        if not file_type:
            raise FileTypeUnknownError(f"无法识别的文件格式：{self.file_path}")
        return file_type

    def _check_file_exists(self) -> None:
        """检查文件是否存在"""
        if not os.path.isfile(self.file_path):
            raise FileNotFoundError(f"文件路径无效或不是文件: {self.file_path}")

    async def _async_check_file_exists(self) -> None:
        """异步检查文件是否存在"""
        await asyncio.to_thread(self._check_file_exists)

    def load(self) -> 'UniversalLoader':
        """同步加载数据"""
        self._check_file_exists()
        try:
            self.data = self._load_data_sync()
        except Exception as e:
            raise LoadError(f"加载文件时出错: {e}")
        return self

    async def aload(self) -> 'UniversalLoader':
        """异步加载数据"""
        await self._async_check_file_exists()
        try:
            self.data = await self._load_data_async()
        except Exception as e:
            raise LoadError(f"异步加载文件时出错: {e}")
        return self

    def save(self, save_path: Optional[str] = None) -> 'UniversalLoader':
        """同步保存数据"""
        try:
            self._save_data_sync(save_path)
        except Exception as e:
            raise SaveError(f"保存文件时出错: {e}")
        return self

    async def asave(self, save_path: Optional[str] = None) -> 'UniversalLoader':
        """异步保存数据"""
        try:
            await self._save_data_async(save_path)
        except Exception as e:
            raise SaveError(f"异步保存文件时出错: {e}")
        return self

    def reload(self) -> 'UniversalLoader':
        """重新加载数据"""
        self.load()
        return self

    async def areload(self) -> 'UniversalLoader':
        """异步重新加载数据"""
        await self.aload()
        return self

    def __getitem__(self, key: str) -> Any:
        """获取数据项"""
        return self.data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """设置数据项"""
        self.data[key] = value

    def __delitem__(self, key: str) -> None:
        """删除数据项"""
        if key in self.data:
            del self.data[key]

    def __str__(self) -> str:
        """返回数据的字符串表示"""
        return str(self.data)

    def keys(self):
        """返回所有键"""
        return self.data.keys()

    def values(self):
        """返回所有值"""
        return self.data.values()

    def items(self):
        """返回所有键值对"""
        return self.data.items()

    # 加载数据
    def _load_data_sync(self) -> Dict[str, Any]:
        """同步加载数据"""
        if self.file_type == 'json':
            with open(self.file_path, 'r') as f:
                return (ujson.load(f) if UJSON_AVAILABLE else json.load(f))
        elif self.file_type == 'toml' and TOML_AVAILABLE:
            with open(self.file_path, 'r') as f:
                return toml.load(f)
        elif self.file_type == 'yaml' and YAML_AVAILABLE:
            with open(self.file_path, 'r') as f:
                return yaml.safe_load(f) or {}
        elif self.file_type == 'ini':
            config = ConfigParser()
            config.read(self.file_path)
            return {s: dict(config[s]) for s in config.sections()}
        elif self.file_type == 'xml':
            tree = ET.parse(self.file_path)
            return self._xml_to_dict(tree.getroot())
        elif self.file_type == 'properties':
            return self._parse_properties()
        elif self.file_type == 'pickle' and PICKLE_AVAILABLE:
            with open(self.file_path, 'rb') as f:
                return pickle.load(f) # type: ignore
        else:
            raise FileTypeUnknownError(f"不支持的文件类型：{self.file_path}")

    async def _load_data_async(self) -> Dict[str, Any]:
        """异步加载数据"""
        if AIOFILES_AVAILABLE:
            async with _open_file(self.file_path, 'r') as f:
                content = await f.read()
                if self.file_type == 'json':
                    return (ujson.loads(content) if UJSON_AVAILABLE else json.loads(content))
                elif self.file_type == 'toml' and TOML_AVAILABLE:
                    return toml.loads(content)
                elif self.file_type == 'yaml' and YAML_AVAILABLE:
                    return yaml.safe_load(content) or {}
                else:
                    return await asyncio.to_thread(self._load_data_sync)
        else:
            return await asyncio.to_thread(self._load_data_sync)

    # 保存数据
    def _save_data_sync(self, save_path: Optional[str] = None) -> None:
        """同步保存数据"""
        save_path = save_path if save_path is not None else self.file_path
        if self.file_type == 'json':
            with open(save_path, 'w') as f:
                if UJSON_AVAILABLE:
                    ujson.dump(self.data, f, ensure_ascii=False, indent=4)
                else:
                    json.dump(self.data, f, ensure_ascii=False, indent=4)
        elif self.file_type == 'toml' and TOML_AVAILABLE:
            with open(save_path, 'w') as f:
                toml.dump(self.data, f)
        elif self.file_type == 'yaml' and YAML_AVAILABLE:
            with open(save_path, 'w') as f:
                yaml.dump(self.data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        elif self.file_type == 'ini':
            config = ConfigParser()
            for section, items in self.data.items():
                config[section] = items
            with open(save_path, 'w') as f:
                config.write(f)
        elif self.file_type == 'xml':
            root = ET.Element('root')
            self._dict_to_xml(root, self.data)
            ET.ElementTree(root).write(save_path, encoding='utf-8', xml_declaration=True)
        elif self.file_type == 'properties':
            with open(save_path, 'w') as f:
                for k, v in self.data.items():
                    f.write(f"{k}={v}\n")
        elif self.file_type == 'pickle' and PICKLE_AVAILABLE:
            with open(save_path, 'wb') as f:
                pickle.dump(self.data, f) # type: ignore
        else:
            raise FileTypeUnknownError(f"不支持的文件类型：{self.file_path}")

    async def _save_data_async(self, save_path: Optional[str] = None) -> None:
        """异步保存数据"""
        save_path = save_path if save_path is not None else self.file_path
        if self.file_type == 'json':
            serialized = ujson.dumps(self.data, ensure_ascii=False, indent=4) if UJSON_AVAILABLE else json.dumps(self.data, ensure_ascii=False, indent=4)
            async with _open_file(save_path, 'w') as f:
                await f.write(serialized)
        elif self.file_type == 'toml' and TOML_AVAILABLE:
            async with _open_file(save_path, 'w') as f:
                await f.write(toml.dumps(self.data))
        elif self.file_type == 'yaml' and YAML_AVAILABLE:
            yaml_output = yaml.dump(self.data, allow_unicode=True, default_flow_style=False, sort_keys=False)
            async with _open_file(save_path, 'w') as f:
                await f.write(yaml_output)
        else:
            await asyncio.to_thread(self._save_data_sync, save_path)

    # XML 转字典 / 字典转 XML
    def _xml_to_dict(self, element: ET.Element) -> Dict:
        """将 XML 元素转换为字典"""
        result = {**element.attrib}
        for child in element:
            key = child.tag
            child_dict = self._xml_to_dict(child)
            if key in result:
                if isinstance(result[key], list):
                    result[key].append(child_dict)
                else:
                    result[key] = [result[key], child_dict]
            else:
                result[key] = child_dict
        return result

    def _dict_to_xml(self, parent: ET.Element, data: Dict) -> None:
        """将字典转换为 XML 元素"""
        for key, value in data.items():
            if isinstance(value, dict):
                child = ET.SubElement(parent, key)
                self._dict_to_xml(child, value)
            elif isinstance(value, list):
                for item in value:
                    child = ET.SubElement(parent, key)
                    self._dict_to_xml(child, item)
            else:
                child = ET.SubElement(parent, key)
                child.text = str(value)

    # Properties 文件解析
    def _parse_properties(self) -> Dict[str, Any]:
        """解析 Properties 文件"""
        data = {}
        with open(self.file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('') and not line.startswith('!'):
                    parts = line.split('=', 1)
                    data[parts[0].strip()] = parts[1].strip() if len(parts) > 1 else ''
        return data