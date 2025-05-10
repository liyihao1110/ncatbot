"""Plugin management commands for NcatBot CLI."""

import os
import re
import shutil
from typing import Dict, Optional

import requests

from ncatbot.cli.registry import registry
from ncatbot.cli.utils import (
    get_plugin_info_by_name,
)
from ncatbot.plugin import install_plugin_dependencies
from ncatbot.utils import PLUGIN_BROKEN_MARK, get_proxy_url


def get_plugin_index() -> Optional[Dict]:
    """Get the plugin index from the official repository."""
    try:
        index_url = f"{get_proxy_url()}https://raw.githubusercontent.com/ncatbot/NcatBot-Plugins/main/index.json"
        response = requests.get(index_url)
        if response.status_code != 200:
            print(f"获取插件索引失败: {response.status_code}")
            return None
        return response.json()
    except Exception as e:
        print(f"获取插件索引时出错: {e}")
        return None


def gen_plugin_download_url(plugin: str, version: str, repository: str) -> str:
    """Generate the download URL for a plugin version.

    Args:
        plugin: Plugin name
        version: Plugin version
        repository: Plugin repository URL
    """

    def check_url_exists(url):
        """
        检查 URL 是否存在（返回 200 状态码），不下载完整内容
        """
        try:
            # 使用 stream=True，避免立即下载响应体
            response = requests.get(url, stream=True, timeout=5)
            # 立即关闭响应，避免下载内容
            response.close()
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"检查 URL 失败: {url}, 错误: {e}")
            return False

    repo_path = repository.replace("https://github.com/", "")
    url1 = f"{get_proxy_url()}https://github.com/{repo_path}/raw/refs/heads/v{version}/release/{plugin}-{version}.zip"
    url2 = f"{get_proxy_url()}https://github.com/{repo_path}/releases/download/v{version}/{plugin}-{version}.zip"
    if check_url_exists(url1):
        return url1
    elif check_url_exists(url2):
        return url2
    else:
        raise Exception(f"无法找到插件 {plugin} 的下载地址, {url1}, {url2} 均无效")


@registry.register("install", "安装插件", "install <插件名> [--fix]", aliases=["i"])
def install(plugin: str, *args: str) -> bool:
    """Install or update a plugin."""

    def get_versions():
        index = get_plugin_index()
        if not index:
            return False, []

        plugins = index.get("plugins", {})
        if plugin not in plugins:
            print(f"插件 {plugin} 不存在于官方仓库中")
            return False, []

        plugin_info = plugins[plugin]
        versions = plugin_info.get("versions", [])
        repository = plugin_info.get("repository", "")
        if not versions:
            print(f"插件 {plugin} 没有可用的版本")
            return False, []

        return True, versions, repository

    def install_plugin(version, repository):
        def download_file(url, file_name):
            print("Downloading file:", url)
            response = requests.get(url)
            if response.status_code != 200:
                print(f"下载插件包失败: {response.status_code}")
                return False
            with open(file_name, "wb") as f:
                f.write(response.content)
            return True

        print("正在下载插件包...")
        print(os.path.abspath(f"plugins/{plugin}.zip"))
        download_file(
            gen_plugin_download_url(plugin, version, repository),
            f"plugins/{plugin}.zip",
        )
        print("正在解压插件包...")
        directory_path = f"plugins/{plugin}"
        os.makedirs(directory_path, exist_ok=True)
        shutil.unpack_archive(f"{directory_path}.zip", directory_path)
        os.remove(f"{directory_path}.zip")
        install_plugin_dependencies(plugin)

    fix = args[0] == "--fix" if len(args) else False

    os.makedirs("plugins", exist_ok=True)
    print(f"正在尝试安装插件: {plugin}")
    status, versions, repository = get_versions()
    if not status:
        return False

    latest_version = versions[0]
    exist, current_version = get_plugin_info_by_name(plugin)
    if exist and not fix:
        if current_version == latest_version:
            print(f"插件 {plugin} 已经是最新版本: {current_version}")
            return
        print(
            f"插件 {plugin} 已经安装, 当前版本: {current_version}, 最新版本: {latest_version}"
        )
        if input(f"是否更新插件 {plugin} (y/n): ").lower() not in ["y", "yes"]:
            return
        shutil.rmtree(f"plugins/{plugin}")
    print(f"正在安装插件 {plugin}-{latest_version}...")
    install_plugin(latest_version, repository)
    print(f"插件 {plugin}-{latest_version} 安装成功!")


@registry.register(
    "create", "创建插件模板", "create <插件名>", aliases=["new", "template"]
)
def create_plugin_template(plugin_name: str) -> None:
    """Create a new plugin template with the given name."""
    # Validate plugin name
    if not re.match(r"^[A-Za-z][A-Za-z0-9_]*$", plugin_name):
        print(
            f"插件名 '{plugin_name}' 不合法! 插件名必须以字母开头，只能包含字母、数字和下划线。"
        )
        return

    # Create plugins directory if it doesn't exist
    os.makedirs("plugins", exist_ok=True)

    # Create plugin directory
    plugin_dir = os.path.join("plugins", plugin_name)
    if os.path.exists(plugin_dir):
        print(f"插件目录 '{plugin_dir}' 已存在!")
        if input("是否覆盖? (y/n): ").lower() not in ["y", "yes"]:
            return
        # Remove existing directory
        shutil.rmtree(plugin_dir)

    os.makedirs(plugin_dir)

    # Create __init__.py
    with open(os.path.join(plugin_dir, "__init__.py"), "w", encoding="utf-8") as f:
        f.write(
            f"""from .main import {plugin_name}

__all__ = ["{plugin_name}"]
"""
        )

    # Create main.py
    with open(os.path.join(plugin_dir, "main.py"), "w", encoding="utf-8") as f:
        f.write(
            f"""import os

from ncatbot.plugin import BasePlugin, CompatibleEnrollment
from ncatbot.core import GroupMessage, PrivateMessage, BaseMessage

bot = CompatibleEnrollment  # 兼容回调函数注册器


class {plugin_name}(BasePlugin):
    name = "{plugin_name}"  # 插件名称
    version = "0.0.1"  # 插件版本
    author = "Your Name"  # 插件作者
    info = "这是一个示例插件，用于演示插件系统的基本功能"  # 插件描述
    dependencies = {{}}  # 插件依赖，格式: {{"插件名": "版本要求"}}

    @bot.group_event()
    async def on_group_event(self, msg: GroupMessage):
        # 群消息事件处理
        if msg.raw_message == "测试":
            await self.api.post_group_msg(msg.group_id, text="{plugin_name} 插件测试成功喵")

    @bot.private_event()
    async def on_private_event(self, msg: PrivateMessage):
        # 好友消息事件处理
        if msg.raw_message == "测试":
            await self.api.post_private_msg(msg.user_id, text="{plugin_name} 插件测试成功喵")

    async def on_load(self):
        # 插件加载时执行的操作
        print(f"{{self.name}} 插件已加载")
        print(f"插件版本: {{self.version}}")

        # 注册功能示例
        self.register_user_func(
            name="test",
            handler=self.test_handler,
            prefix="/test",
            description="测试功能",
            usage="/test",
            examples=["/test"],
            tags=["test", "example"],
            metadata={{"category": "utility"}}
        )

        # 注册配置项示例
        self.register_config(
            key="greeting",
            default="你好",
            on_change=self.on_greeting_change,
            description="问候语",
            value_type="string",
            allowed_values=["你好", "Hello", "Hi"],
            metadata={{"category": "greeting", "max_length": 20}}
        )

    async def test_handler(self, msg: BaseMessage):
        # 测试功能处理函数
        await msg.reply_text(f"测试功能调用成功！当前问候语: {{self.config["greeting"]}}")

    async def on_greeting_change(self, value, msg: BaseMessage):
        # 配置变更回调函数
        await msg.reply_text(f"问候语已修改为: {{value}}")
"""
        )

    # Create README.md
    with open(os.path.join(plugin_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(
            f"""# {plugin_name} 插件

## 简介

这是一个 NcatBot 插件模板。

## 功能

- 群消息事件处理
- 好友消息事件处理
- 测试功能 (/test)

## 使用方法

1. 在群聊中发送 "测试" 消息
2. 在私聊中发送 "测试" 消息
3. 使用 `/test` 命令测试功能

## 配置项

- `greeting`: 问候语，默认值为 "你好"，可选值: ["你好", "Hello", "Hi"]

## 依赖

- NcatBot

## 作者

Your Name

## 许可证

MIT
"""
        )

    # Create .gitignore
    with open(os.path.join(plugin_dir, ".gitignore"), "w", encoding="utf-8") as f:
        f.write(
            """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        )

    # Create requirements.txt
    with open(os.path.join(plugin_dir, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write(
            """# 插件依赖项
# 例如: requests==2.28.1
"""
        )

    print(f"插件模板 '{plugin_name}' 创建成功!")
    print(f"插件目录: {os.path.abspath(plugin_dir)}")
    print("请编辑 main.py 文件来实现插件功能。")


@registry.register("remove", "卸载插件", "remove <插件名>", aliases=["r", "uninstall"])
def remove_plugin(plugin: str) -> None:
    """Remove a plugin."""
    plugins = list_plugin(False)
    if plugins.get(plugin, PLUGIN_BROKEN_MARK) == PLUGIN_BROKEN_MARK:
        print(f"插件 {plugin} 不存在!")
        return

    shutil.rmtree(f"plugins/{plugin}")
    print(f"插件 {plugin} 卸载成功!")


@registry.register("list", "列出已安装插件", "list", aliases=["l", "ls"])
def list_plugin(enable_print: bool = True) -> Dict[str, str]:
    """List all installed plugins."""
    dirs = os.listdir("plugins")
    plugins = {}
    for dir in dirs:
        try:
            version = get_plugin_info_by_name(dir)[1]
            plugins[dir] = version
        except Exception:
            plugins[dir] = PLUGIN_BROKEN_MARK
    if enable_print:
        if len(plugins) > 0:
            max_dir_length = max([len(dir) for dir in plugins.keys()])
            print(f"插件目录{' ' * (max_dir_length - 3)}\t版本")
            for dir, version in plugins.items():
                print(f"{dir.ljust(max_dir_length)}\t{version}")
        else:
            print("没有安装任何插件!\n\n")
    return plugins


@registry.register("list_remote", "列出远程可用插件", "list_remote", aliases=["lr"])
def list_remote_plugins() -> None:
    """List available plugins from the official repository."""
    try:
        # 获取插件索引
        index_url = f"{get_proxy_url()}https://raw.githubusercontent.com/ncatbot/NcatBot-Plugins/main/index.json"
        response = requests.get(index_url)
        if response.status_code != 200:
            print(f"获取插件列表失败: {response.status_code}")
            return

        index_data = response.json()
        plugins = index_data.get("plugins", {})

        if not plugins:
            print("没有找到可用的插件")
            return

        # 计算最大长度用于对齐
        max_name_length = max(len(name) for name in plugins.keys())
        max_author_length = max(
            len(plugin.get("author", "")) for plugin in plugins.values()
        )

        # 打印表头
        print(
            f"{'插件名'.ljust(max_name_length)}\t{'作者'.ljust(max_author_length)}\t描述"
        )
        print("-" * (max_name_length + max_author_length + 50))

        # 打印每个插件的信息
        for name, plugin in sorted(plugins.items()):
            author = plugin.get("author", "未知")
            description = plugin.get("description", "无描述")
            print(
                f"{name.ljust(max_name_length)}\t{author.ljust(max_author_length)}\t{description}"
            )

    except Exception as e:
        print(f"获取插件列表时出错: {e}")
