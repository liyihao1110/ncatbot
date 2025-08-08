"""插件管理工具函数。"""

from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union

import requests
from requests.exceptions import RequestException, Timeout

from ncatbot.cli.utils.colors import command, error, header, info, success
from ncatbot.cli.utils.constants import PLUGIN_INDEX_URL
from ncatbot.utils import get_log, get_proxy_url


class PluginInfo(TypedDict):
    versions: List[str]
    repository: str
    name: str


class PluginIndex(TypedDict):
    plugins: Dict[str, PluginInfo]


logger = get_log("CLI")


def get_plugin_index() -> Optional[PluginIndex]:
    """从官方仓库获取插件索引。

    Returns:
        Optional[PluginIndex]: 插件索引，如果获取失败则返回 None
    """
    try:
        proxy_url = get_proxy_url()
        if proxy_url:
            index_url = f"{proxy_url}{PLUGIN_INDEX_URL}"
        else:
            index_url = PLUGIN_INDEX_URL

        logger.debug(f"正在获取插件索引: {index_url}")
        response = requests.get(index_url, timeout=10)
        if response.status_code != 200:
            logger.error(f"获取插件索引失败: HTTP {response.status_code}")
            return None

        data = response.json()
        if not isinstance(data, dict) or "plugins" not in data:
            logger.error("获取的插件索引格式无效")
            return None

        return data
    except Timeout:
        logger.error("获取插件索引超时")
        return None
    except RequestException as e:
        logger.error(f"获取插件索引网络错误: {e}")
        return None
    except ValueError as e:
        logger.error(f"解析插件索引 JSON 失败: {e}")
        return None
    except Exception as e:
        logger.error(f"获取插件索引时出错: {e}")
        return None


def gen_plugin_download_url(plugin_name: str, version: str, repository: str) -> str:
    """生成插件版本的下载 URL。

    Args:
        plugin_name: 插件名称
        version: 插件版本
        repository: 插件仓库 URL

    Returns:
        str: 插件的下载 URL

    Raises:
        Exception: 如果找不到有效的下载 URL
    """

    def check_url_exists(url: str) -> bool:
        """检查 URL 是否存在（返回 200 状态码）。"""
        try:
            logger.debug(f"检查 URL 是否存在: {url}")
            response = requests.get(url, stream=True, timeout=5)
            exists = response.status_code == 200
            response.close()
            return exists
        except (RequestException, Timeout) as e:
            logger.error(f"URL 检查失败: {url}, 错误: {e}")
            return False

    # 确保 proxy_url 以 / 结尾
    proxy_url = get_proxy_url() or ""
    if proxy_url and not proxy_url.endswith("/"):
        proxy_url = f"{proxy_url}/"

    # 清理仓库路径
    repo_path = repository.replace("https://github.com/", "").strip("/")

    # 构建两种可能的下载 URL
    url1 = f"{proxy_url}https://github.com/{repo_path}/raw/refs/heads/v{version}/release/{plugin_name}-{version}.zip"
    url2 = f"{proxy_url}https://github.com/{repo_path}/releases/download/v{version}/{plugin_name}-{version}.zip"

    logger.debug(f"尝试下载 URL 1: {url1}")
    if check_url_exists(url1):
        return url1

    logger.debug(f"尝试下载 URL 2: {url2}")
    if check_url_exists(url2):
        return url2

    raise Exception(f"找不到插件 {plugin_name} v{version} 的下载 URL")


def download_plugin_file(plugin_info: PluginInfo, file_name: str) -> bool:
    """从给定 URL 下载插件文件。

    Args:
        plugin_info: 插件信息，必须包含 name、versions 和 repository 字段
        file_name: 目标文件名

    Returns:
        bool: 下载成功返回 True，否则返回 False
    """
    try:
        # 验证插件信息完整性
        if not plugin_info.get("versions"):
            logger.error(f"插件 {plugin_info.get('name', '未知')} 没有可用版本")
            return False

        plugin_name = plugin_info.get("name")
        version = plugin_info["versions"][0]
        repository = plugin_info.get("repository")

        if not (plugin_name and repository):
            logger.error("插件信息不完整")
            return False

        # 获取下载 URL
        url = gen_plugin_download_url(plugin_name, version, repository)
        logger.info(f"正在下载插件: {plugin_name} v{version}")

        # 下载文件
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            logger.error(f"下载插件包失败: HTTP {response.status_code}")
            return False

        with open(file_name, "wb") as f:
            f.write(response.content)

        logger.info(f"插件下载完成: {file_name}")
        return True
    except Timeout:
        logger.error("下载插件包超时")
        return False
    except RequestException as e:
        logger.error(f"下载插件包网络错误: {e}")
        return False
    except Exception as e:
        logger.error(f"下载插件包时出错: {e}")
        return False


def get_plugin_versions(
    plugin_name: str,
) -> Tuple[bool, Union[PluginInfo, Dict[str, Any]]]:
    """获取插件的可用版本。

    Args:
        plugin_name: 插件名称

    Returns:
        Tuple[bool, Union[PluginInfo, Dict]]: (成功标志, 插件信息)
            成功时返回 (True, 插件信息)
            失败时返回 (False, 空字典)
    """
    # 获取插件索引
    index = get_plugin_index()
    if not index:
        logger.error("无法获取插件索引")
        return False, {}

    # 检查插件是否存在
    plugins = index["plugins"]
    if plugin_name not in plugins:
        logger.error(f"插件 {plugin_name} 不存在于官方仓库")
        return False, {}

    # 获取插件信息
    plugin_info = plugins[plugin_name]

    # 检查是否有可用版本
    if not plugin_info.get("versions"):
        logger.error(f"插件 {plugin_name} 没有可用版本")
        return False, {}

    return True, plugin_info


# 计算字符显示宽度的函数 - 中文字符占用两个宽度单位
def get_display_width(s: str) -> int:
    """计算字符串在终端中的显示宽度，中文字符占用两个宽度。

    Args:
        s: 要计算宽度的字符串

    Returns:
        int: 字符串的显示宽度
    """
    width = 0
    for char in s:
        if "\u4e00" <= char <= "\u9fff":
            width += 2
        else:
            width += 1
    return width


def format_plugin_table(
    plugins: Dict[str, Union[Dict[str, Any], PluginInfo, str]],
    mode: str = "local",
    broken_mark: str = "plugin broken",
    show_plugins_dir: Optional[str] = None,
) -> str:
    """格式化并输出插件列表表格。

    Args:
        plugins: 插件字典
            - 当 mode="local" 时，格式为 {插件名: 元数据字典或版本字符串}
            - 当 mode="remote" 时，格式为 {插件名: 插件信息字典}
        mode: 模式，"local" 表示本地插件，"remote" 表示远程插件
        broken_mark: 标记插件损坏的字符串，仅在 mode="local" 时使用
        show_plugins_dir: 可选的插件目录路径，当提供时会在表格上方显示

    Returns:
        str: 格式化后的插件列表字符串，为空字符串时表示没有插件
    """
    if not plugins:
        return ""

    output_lines = []

    # 显示插件目录信息（如果提供）
    if show_plugins_dir:
        output_lines.append(f"插件目录: {info(show_plugins_dir)}")
        output_lines.append("")

    # 准备数据结构
    formatted_plugins = {}

    if mode == "local":
        # 处理本地插件数据
        for name, data in plugins.items():
            if isinstance(data, str) and data == broken_mark:
                # 处理损坏的插件
                formatted_plugins[name] = {
                    "name": name,
                    "author": "Unknown",
                    "description": error("插件损坏"),
                    "version": error(broken_mark),
                }
            elif isinstance(data, str):
                # 处理只有版本号的插件
                formatted_plugins[name] = {
                    "name": name,
                    "author": "Unknown",
                    "description": "无描述",
                    "version": data,
                }
            else:
                # 处理有完整元数据的插件
                metadata = data
                formatted_plugins[name] = {
                    "name": name,
                    "author": metadata.get("author", "Unknown"),
                    "description": metadata.get("description", "无描述"),
                    "version": metadata.get("version", "Unknown"),
                }
    else:  # mode == "remote"
        # 处理远程插件数据
        for name, data in plugins.items():
            latest_version = (
                data.get("versions", ["Unknown"])[0]
                if "versions" in data
                else "Unknown"
            )
            formatted_plugins[name] = {
                "name": name,
                "author": data.get("author", "Unknown"),
                "description": data.get("description", "无描述"),
                "version": latest_version,
            }

    # 计算最大显示宽度
    max_name_width = max(get_display_width(name) for name in formatted_plugins.keys())
    max_author_width = max(
        get_display_width(plugin.get("author", "Unknown"))
        for plugin in formatted_plugins.values()
    )

    # 设置列宽
    name_column_width = max(max_name_width, 8) + 2
    author_column_width = max(max_author_width, 8) + 2

    # 表头
    name_text = "插件名"
    author_text = "作者"
    version_text = "版本"
    desc_text = "描述"

    name_text_width = get_display_width(name_text)
    author_text_width = get_display_width(author_text)
    version_text_width = get_display_width(version_text)

    name_header = header(name_text) + " " * (name_column_width - name_text_width)
    author_header = header(author_text) + " " * (
        author_column_width - author_text_width
    )

    output_lines.append(
        f"{name_header}  {author_header}  {header(version_text)}  {header(desc_text)}"
    )

    # 分隔线
    separator_width = name_column_width + author_column_width + 50
    output_lines.append("─" * separator_width)

    # 插件行
    for name, plugin in sorted(formatted_plugins.items()):
        author = plugin.get("author", "Unknown")
        description = plugin.get("description", "无描述")
        version = plugin.get("version", "Unknown")

        name_width = get_display_width(name)
        author_width = get_display_width(author)

        name_padding = name_column_width - name_width
        author_padding = author_column_width - author_width

        name_col = command(name) + " " * name_padding
        author_col = info(author) + " " * author_padding

        output_lines.append(
            f"{name_col}  {author_col}  {success(version)}  {description}"
        )

    return "\n".join(output_lines)
