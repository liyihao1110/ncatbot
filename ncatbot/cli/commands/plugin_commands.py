"""Plugin management commands for NcatBot CLI."""

import os
import re
import shutil
from typing import Dict

from ncatbot.cli.commands.registry import registry
from ncatbot.cli.utils import (
    download_plugin_file,
    get_plugin_versions,
    install_pip_dependencies,
)
from ncatbot.plugin import get_plugin_info_by_name
from ncatbot.utils import ncatbot_config as config

# Template paths
PLUGIN_BROKEN_MARK = "plugin broken"
TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "utils", "assets", "templates"
)
TEMPLATE_FILES = {
    "__init__.py": os.path.join(TEMPLATE_DIR, "__init__.py"),
    "main.py": os.path.join(TEMPLATE_DIR, "main.py"),
    "README.md": os.path.join(TEMPLATE_DIR, "README.md"),
    ".gitignore": os.path.join(TEMPLATE_DIR, ".gitignore"),
    "requirements.txt": os.path.join(TEMPLATE_DIR, "requirements.txt"),
}


@registry.register(
    "install",
    "安装插件",
    "install <插件名> [--force_install]",
    aliases=["i"],
    category="Plugin",
)
def install(plugin: str, *args: str) -> bool:
    """Install or update a plugin."""
    force_install = args[0] == "-f" if len(args) else False
    if force_install:
        print(f"正在强制安装插件: {plugin}")
        if os.path.exists(f"{config.plugin.plugins_dir}/{plugin}"):
            shutil.rmtree(f"{config.plugin.plugins_dir}/{plugin}")
    else:
        print(f"正在尝试安装插件: {plugin}")

    plugin_status, plugin_info = get_plugin_versions(plugin)
    if not plugin_status:
        print(f"插件 {plugin} 不存在!")
        return False

    latest_version = plugin_info["versions"][0]
    exist, meta = get_plugin_info_by_name(plugin)
    if exist:
        if meta["version"] == latest_version:
            print(f"插件 {plugin} 已经是最新版本: {meta['version']}")
            return
        print(
            f"插件 {plugin} 已经安装, 当前版本: {meta['version']}, 最新版本: {latest_version}"
        )
        if input(f"是否更新插件 {plugin} (y/n): ").lower() not in ["y", "yes"]:
            return
        shutil.rmtree(f"{config.plugin.plugins_dir}/{plugin}")

    try:
        print(f"正在安装插件 {plugin}-{latest_version}...")
        os.makedirs(config.plugin.plugins_dir, exist_ok=True)
        if not download_plugin_file(
            plugin_info, f"{config.plugin.plugins_dir}/{plugin}.zip"
        ):
            return False

        print("正在解压插件包...")
        directory_path = f"{config.plugin.plugins_dir}/{plugin}"
        os.makedirs(directory_path, exist_ok=True)
        shutil.unpack_archive(f"{directory_path}.zip", directory_path)
        os.remove(f"{directory_path}.zip")
        install_pip_dependencies(os.path.join(directory_path, "requirements.txt"))
        print(f"插件 {plugin}-{latest_version} 安装成功!")
    except Exception as e:
        print(f"安装插件时出错: {e}")
        return False


@registry.register(
    "create",
    "创建插件模板",
    "create <插件名>",
    aliases=["new", "template"],
    category="Plugin",
)
def create_plugin_template(name: str) -> None:
    """Create a new plugin template.

    Args:
        name: Plugin name
    """
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", name):
        print(
            f"插件名 '{name}' 不合法! 插件名必须以字母开头，只能包含字母、数字和下划线。"
        )
        return

    plugin_dir = os.path.join(config.plugin.plugins_dir, name)
    if os.path.exists(plugin_dir):
        print(f"插件目录 '{name}' 已存在!")
        if input("是否覆盖? (y/n): ").lower() not in ["y", "yes"]:
            return
        shutil.rmtree(plugin_dir)

    os.makedirs(plugin_dir, exist_ok=True)

    # Get author name
    author = input("请输入作者名称 (默认: Your Name): ").strip() or "Your Name"

    # Copy template files
    for filename, template_path in TEMPLATE_FILES.items():
        target_path = os.path.join(plugin_dir, filename)
        shutil.copy2(template_path, target_path)

        # Replace placeholders in template files
        if filename in ["__init__.py", "main.py", "README.md"]:
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read()

            content = content.replace("Plugin Name", name)
            content = content.replace("Your Name", author)
            content = content.replace(
                "Plugin description", f"{name} plugin for NcatBot"
            )

            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)

    print(f"插件模板 '{name}' 创建成功!")
    print(f"插件目录: {plugin_dir}")
    print("请修改插件信息并添加功能代码。")


@registry.register(
    "remove",
    "卸载插件",
    "remove <插件名>",
    aliases=["r", "uninstall"],
    category="Plugin",
)
def remove_plugin(plugin: str) -> None:
    """Remove a plugin."""
    plugins = list_plugins(False)
    if plugins.get(plugin, PLUGIN_BROKEN_MARK) == PLUGIN_BROKEN_MARK:
        print(f"插件 {plugin} 不存在!")
        return

    shutil.rmtree(f"{config.plugin.plugins_dir}/{plugin}")
    print(f"插件 {plugin} 卸载成功!")


@registry.register(
    "list",
    "列出已安装插件",
    "list",
    aliases=["l", "ls"],
    category="Plugin",
)
def list_plugins(enable_print: bool = True) -> Dict[str, str]:
    """List all installed plugins."""
    dirs = os.listdir(config.plugin.plugins_dir)
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


@registry.register(
    "list_remote",
    "列出远程可用插件",
    "list_remote",
    aliases=["lr"],
    category="Plugin",
)
def list_remote_plugins() -> None:
    """List available plugins from the official repository."""
    try:
        from ncatbot.cli.utils import get_plugin_index

        index_data = get_plugin_index()
        if not index_data:
            return

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
