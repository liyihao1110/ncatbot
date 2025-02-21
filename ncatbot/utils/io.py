import asyncio
import base64
import json
import os
import pickle
import warnings
import xml.etree.ElementTree as ET
from configparser import ConfigParser
from pathlib import Path
from typing import Any, Dict, Optional, Union

import httpx


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


# ---------------------
# region 模块可用性检测区块
# ---------------------
# PICKLE
PICKLE_AVAILABLE = False

# TOML 模块检测
TOML_AVAILABLE = False
try:
    import toml  # type: ignore

    TOML_AVAILABLE = True
except ImportError:
    warnings.warn("toml 模块未安装。TOML 功能将被禁用。", ImportWarning)

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
    pass  # 非关键依赖，静默处理

# 高性能JSON模块检测
UJSON_AVAILABLE = False
try:
    import ujson  # type: ignore

    UJSON_AVAILABLE = True
except ImportError:
    pass  # 回退到标准json模块
# endregion

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


class UniversalLoader:
    def __init__(self, file_path: Union[str, Path], file_type: Optional[str] = None):
        """
        初始化通用加载器
        :param file_path: 文件路径
        :param file_type: 可选参数，手动指定文件类型（覆盖自动检测）
        """
        # 统一路径为 Path 类型
        self.file_path: Path = Path(file_path).resolve()  # 获取绝对路径
        self.data: Dict[str, Any] = {}
        self.file_type = file_type.lower() if file_type else self._detect_file_type()
        self._async_lock = asyncio.Lock()

    def _detect_file_type(self) -> str:
        """通过文件扩展名检测文件类型"""
        file_type_map = {
            "json": "json",
            "toml": "toml",
            "yaml": "yaml",
            "yml": "yaml",
            "ini": "ini",
            "xml": "xml",
            "properties": "properties",
            "pickle": "pickle",
        }
        # 使用 Path 的 suffix 属性获取扩展名
        ext = self.file_path.suffix.lower().lstrip(".") if self.file_path.suffix else ""
        file_type = file_type_map.get(ext, None)
        if not file_type:
            raise FileTypeUnknownError(f"无法识别的文件格式：{self.file_path}")
        return file_type

    # ---------------------
    # region文件存在性检查方法
    # ---------------------

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
        """同步加载数据"""
        self._check_file_exists()
        try:
            self.data = self._load_data_sync()
        except Exception as e:
            raise LoadError(f"加载文件时出错: {e}") from e
        return self

    async def aload(self) -> "UniversalLoader":
        """异步加载数据（带锁保护）"""
        await self._async_check_file_exists()
        async with self._async_lock:
            try:
                self.data = await self._load_data_async()
            except Exception as e:
                raise LoadError(f"异步加载文件时出错: {e}") from e
        return self

    def save(self, save_path: Optional[Union[str, Path]] = None) -> "UniversalLoader":
        """同步保存数据"""
        save_path = Path(save_path).resolve() if save_path else self.file_path
        try:
            self._save_data_sync(str(save_path))  # 暂时传递字符串
        except Exception as e:
            raise SaveError(f"保存文件时出错: {e}") from e
        return self

    async def asave(
        self, save_path: Optional[Union[str, Path]] = None
    ) -> "UniversalLoader":
        """异步保存数据（带锁保护）"""
        save_path = Path(save_path).resolve() if save_path else self.file_path
        async with self._async_lock:
            try:
                await self._save_data_async(str(save_path))  # 异步保存时传递字符串
            except Exception as e:
                raise SaveError(f"异步保存文件时出错: {e}") from e
        return self

    # endregion

    # ---------------------
    # region 数据访问相关魔术方法
    # ---------------------

    def __getitem__(self, key: str) -> Any:
        """字典式数据访问"""
        return self.data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """字典式数据设置"""
        self.data[key] = value

    def __delitem__(self, key: str) -> None:
        """字典式数据删除"""
        if key in self.data:
            del self.data[key]

    def __str__(self) -> str:
        """友好的字符串表示"""
        return str(self.data)

    def get(self, key, default=None):
        """安全获取数据方法"""
        return self.data.get(key, default)

    def keys(self):
        """获取所有键"""
        return self.data.keys()

    def values(self):
        """获取所有值"""
        return self.data.values()

    def items(self):
        """获取所有键值对"""
        return self.data.items()

    # endregion

    # ---------------------
    # region 数据加载实现（同步）
    # ---------------------

    def _load_data_sync(self) -> Dict[str, Any]:
        """根据文件类型选择对应的同步加载方法"""
        if self.file_type == "json":
            with open(self.file_path, "r") as f:
                # 优先使用ujson提升性能
                return ujson.load(f) if UJSON_AVAILABLE else json.load(f)

        elif self.file_type == "toml":
            if not TOML_AVAILABLE:
                raise ModuleNotInstalledError(
                    "请安装 toml 模块以支持 TOML 文件（pip install toml）"
                )
            with open(self.file_path, "r") as f:
                return toml.load(f)

        elif self.file_type == "yaml":
            if not YAML_AVAILABLE:
                raise ModuleNotInstalledError(
                    "请安装 PyYAML 模块以支持 YAML 文件（pip install PyYAML）"
                )
            with open(self.file_path, "r") as f:
                return yaml.safe_load(f) or {}  # 处理空文件情况

        elif self.file_type == "ini":
            config = ConfigParser()
            # 保留键名原始大小写
            config.optionxform = str  # type: ignore
            config.read(self.file_path)
            return {s: dict(config[s]) for s in config.sections()}

        elif self.file_type == "xml":
            tree = ET.parse(self.file_path)
            return self._xml_to_dict(tree.getroot())

        elif self.file_type == "properties":
            return self._parse_properties()

        elif self.file_type == "pickle":
            if not PICKLE_AVAILABLE:
                raise ValueError("请手动开启 pickle 支持以支持 PICKLE 文件")
            with open(self.file_path, "rb") as f:
                return pickle.load(f)

        else:
            raise FileTypeUnknownError(f"不支持的文件类型：{self.file_type}")

    # endregion

    # ---------------------
    # region 数据加载实现（异步）
    # ---------------------

    async def _load_data_async(self) -> Dict[str, Any]:
        """异步加载数据核心逻辑"""
        if AIOFILES_AVAILABLE:
            # 使用aiofiles进行真正的异步文件读取
            async with _open_file(self.file_path, "r") as f:
                content = await f.read()

                if self.file_type == "json":
                    return (
                        ujson.loads(content) if UJSON_AVAILABLE else json.loads(content)
                    )

                elif self.file_type == "toml":
                    if not TOML_AVAILABLE:
                        raise ModuleNotInstalledError(
                            "请安装 toml 模块以支持 TOML 文件"
                        )
                    return toml.loads(content)

                elif self.file_type == "yaml":
                    if not YAML_AVAILABLE:
                        raise ModuleNotInstalledError(
                            "请安装 PyYAML 模块以支持 YAML 文件"
                        )
                    return yaml.safe_load(content) or {}

                else:
                    # 其他格式回落到同步方法（使用线程池）
                    return await asyncio.to_thread(self._load_data_sync)

        else:
            # 无aiofiles时回退到同步方法
            return await asyncio.to_thread(self._load_data_sync)

    # endregion

    # ---------------------
    # region 数据保存实现（同步）
    # ---------------------

    def _save_data_sync(self, save_path: Optional[str] = None) -> None:
        """同步保存数据到文件"""
        save_path = save_path or self.file_path

        if self.file_type == "json":
            with open(save_path, "w") as f:
                if UJSON_AVAILABLE:
                    ujson.dump(self.data, f, ensure_ascii=False, indent=4)
                else:
                    json.dump(self.data, f, ensure_ascii=False, indent=4)

        elif self.file_type == "toml":
            if not TOML_AVAILABLE:
                raise ModuleNotInstalledError("请安装 toml 模块以支持 TOML 文件")
            with open(save_path, "w") as f:
                toml.dump(self.data, f)

        elif self.file_type == "yaml":
            if not YAML_AVAILABLE:
                raise ModuleNotInstalledError("请安装 PyYAML 模块以支持 YAML 文件")
            with open(save_path, "w") as f:
                # 禁用默认的排序和流式风格，保持数据顺序
                yaml.dump(
                    self.data,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                )

        elif self.file_type == "ini":
            config = ConfigParser()
            config.optionxform = str  # 保留键名大小写
            for section, items in self.data.items():
                config[section] = items
            with open(save_path, "w") as f:
                config.write(f)

        elif self.file_type == "xml":
            root = ET.Element("root")
            self._dict_to_xml(root, self.data)
            ET.ElementTree(root).write(
                save_path, encoding="utf-8", xml_declaration=True
            )

        elif self.file_type == "properties":
            with open(save_path, "w") as f:
                for k, v in self.data.items():
                    f.write(f"{k}={v}\n")

        elif self.file_type == "pickle":
            if not PICKLE_AVAILABLE:
                raise ValueError("请手动开启 pickle 支持以支持 PICKLE 文件")
            with open(save_path, "wb") as f:
                pickle.dump(self.data, f)

        else:
            raise FileTypeUnknownError(f"不支持的文件类型：{self.file_type}")

    # endregion

    # ---------------------
    # region 数据保存实现（异步）
    # ---------------------

    async def _save_data_async(self, save_path: Optional[str] = None) -> None:
        """异步保存数据到文件"""
        save_path = save_path or self.file_path

        if self.file_type == "json":
            # 先序列化再异步写入
            serialized = (
                ujson.dumps(self.data, ensure_ascii=False, indent=4)
                if UJSON_AVAILABLE
                else json.dumps(self.data, ensure_ascii=False, indent=4)
            )
            async with _open_file(save_path, "w") as f:
                await f.write(serialized)

        elif self.file_type == "toml":
            if not TOML_AVAILABLE:
                raise ModuleNotInstalledError("请安装 toml 模块以支持 TOML 文件")
            async with _open_file(save_path, "w") as f:
                await f.write(toml.dumps(self.data))

        elif self.file_type == "yaml":
            if not YAML_AVAILABLE:
                raise ModuleNotInstalledError("请安装 PyYAML 模块以支持 YAML 文件")
            yaml_output = yaml.dump(
                self.data, allow_unicode=True, default_flow_style=False, sort_keys=False
            )
            async with _open_file(save_path, "w") as f:
                await f.write(yaml_output)

        else:
            # 其他格式回落到同步保存方法
            await asyncio.to_thread(self._save_data_sync, save_path)

    # endregion

    # ---------------------
    # region XML转换工具方法
    # ---------------------

    def _xml_to_dict(self, element: ET.Element) -> Dict:
        """
        将XML元素转换为字典
        :param element: XML元素节点
        :return: 包含节点信息和属性的字典
        """
        result = element.attrib.copy()

        # 如果存在且非空
        if element.text and element.text.strip():
            result["#text"] = element.text.strip()

        # 递归处理子元素
        for child in element:
            key = child.tag
            child_dict = self._xml_to_dict(child)

            # 处理重复标签的情况
            if key in result:
                # 如果已存在相同标签，转换为列表存储
                if isinstance(result[key], list):
                    result[key].append(child_dict)
                else:
                    result[key] = [result[key], child_dict]
            else:
                result[key] = child_dict

        return result

    def _dict_to_xml(self, parent: ET.Element, data: Dict) -> None:
        """
        将字典转换为XML元素
        :param parent: 父XML元素
        :param data: 要转换的字典数据
        """
        for key, value in data.items():
            # 处理文本内容
            if key == "#text":
                parent.text = str(value)
                continue

            # 处理嵌套字典
            if isinstance(value, dict):
                child = ET.SubElement(parent, key)
                self._dict_to_xml(child, value)

            # 处理列表类型数据
            elif isinstance(value, list):
                for item in value:
                    child = ET.SubElement(parent, key)
                    self._dict_to_xml(child, item)

            # 处理简单类型
            else:
                child = ET.SubElement(parent, key)
                child.text = str(value)

    # endregion

    # ---------------------
    # region Properties文件解析
    # ---------------------

    def _parse_properties(self) -> Dict[str, Any]:
        """
        解析Properties格式文件
        :return: 键值对字典
        """
        data = {}
        with open(self.file_path, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # 跳过空行和注释行（以#或!开头）
                if not line or line.startswith("#") or line.startswith("!"):
                    continue

                # 分割键值对（最多分割一次）
                parts = line.split("=", 1)
                key = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ""

                # 处理重复键的情况（保留最后一次出现的值）
                data[key] = value
        return data

    # endregion


# endregion
