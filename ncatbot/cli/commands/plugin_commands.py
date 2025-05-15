"""plugin management commands for NcatBot CLI."""

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
from ncatbot.cli.utils.colors import command, error, header, info, success, warning
from ncatbot.plugin import get_plugin_info_by_name
from ncatbot.utils import ncatbot_config as config

# Constants
PLUGIN_BROKEN_MARK = "plugin broken"

# Template directory path
TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "utils",
    "assets",
    "template_plugin",
)


@registry.register(
    "install",
    "安装插件",
    "install <插件名> [--force_install]",
    aliases=["i"],
    category="plg",
)
def install(plugin: str, *args: str) -> bool:
    """Install or update a plugin."""
    force_install = args[0] == "-f" if len(args) else False
    if force_install:
        print(info(f"正在强制安装插件: {command(plugin)}"))
        if os.path.exists(f"{config.plugin.plugins_dir}/{plugin}"):
            shutil.rmtree(f"{config.plugin.plugins_dir}/{plugin}")
    else:
        print(info(f"正在尝试安装插件: {command(plugin)}"))

    plugin_status, plugin_info = get_plugin_versions(plugin)
    if not plugin_status:
        print(error(f"插件 {command(plugin)} 不存在!"))
        return False

    latest_version = plugin_info["versions"][0]
    exist, meta = get_plugin_info_by_name(plugin)
    if exist:
        if meta["version"] == latest_version:
            print(success(f"插件 {command(plugin)} 已经是最新版本: {meta['version']}"))
            return
        print(
            info(
                f"插件 {command(plugin)} 已经安装, 当前版本: {meta['version']}, 最新版本: {latest_version}"
            )
        )
        if input(warning(f"是否更新插件 {command(plugin)} (y/n): ")).lower() not in [
            "y",
            "yes",
        ]:
            return
        shutil.rmtree(f"{config.plugin.plugins_dir}/{plugin}")

    try:
        print(info(f"正在安装插件 {command(plugin)}-{latest_version}..."))
        os.makedirs(config.plugin.plugins_dir, exist_ok=True)
        if not download_plugin_file(
            plugin_info, f"{config.plugin.plugins_dir}/{plugin}.zip"
        ):
            return False

        print(info("正在解压插件包..."))
        directory_path = f"{config.plugin.plugins_dir}/{plugin}"
        os.makedirs(directory_path, exist_ok=True)
        shutil.unpack_archive(f"{directory_path}.zip", directory_path)
        os.remove(f"{directory_path}.zip")
        install_pip_dependencies(os.path.join(directory_path, "requirements.txt"))
        print(success(f"插件 {command(plugin)}-{latest_version} 安装成功!"))
    except Exception as e:
        print(error(f"安装插件时出错: {e}"))
        return False


@registry.register(
    "create",
    "创建插件模板",
    "create <插件名>",
    aliases=["new", "template"],
    category="plg",
)
def create_plugin_template(
    name: str, author: str = None, non_interactive: bool = False
) -> None:
    """Create a new plugin template.

    Args:
        name: Plugin name
        author: Optional author name
        non_interactive: Whether to run in non-interactive mode
    """
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", name):
        print(
            error(
                f"插件名 '{command(name)}' 不合法! 插件名必须以字母开头，只能包含字母、数字和下划线。"
            )
        )
        return

    # 确保插件目录存在
    try:
        os.makedirs(config.plugin.plugins_dir, exist_ok=True)
    except Exception as e:
        print(error(f"无法创建插件目录: {e}"))
        return

    plugin_dir = os.path.join(config.plugin.plugins_dir, name)
    if os.path.exists(plugin_dir):
        print(warning(f"插件目录 '{command(name)}' 已存在!"))
        if not non_interactive and input(warning("是否覆盖? (y/n): ")).lower() not in [
            "y",
            "yes",
        ]:
            return
        shutil.rmtree(plugin_dir)

    try:
        os.makedirs(plugin_dir, exist_ok=True)

        # Get author name if not provided
        if author is None:
            if non_interactive:
                author = "Your Name"
            else:
                author_input = input(info("请输入作者名称 (默认: Your Name): ")).strip()
                author = author_input if author_input else "Your Name"

        # 检查模板目录
        if not os.path.exists(TEMPLATE_DIR):
            print(error(f"模板目录不存在: {TEMPLATE_DIR}"))
            return

        # 首先复制所有模板文件
        for file in os.listdir(TEMPLATE_DIR):
            src_path = os.path.join(TEMPLATE_DIR, file)
            dst_path = os.path.join(plugin_dir, file)

            if os.path.isfile(src_path):
                # 复制文件
                shutil.copy2(src_path, dst_path)

        # 然后处理需要替换的文件内容
        replacements = {
            "main.py": {
                "Plugin Name": name,
                "Your Name": author,
                # 确保只替换类定义的Plugin，而不是其他地方的Plugin
                "class Plugin(BasePlugin)": f"class {name}(BasePlugin)",
            },
            "__init__.py": {
                "from .main import Plugin": f"from .main import {name}",
                '__all__ = ["Plugin"]': f'__all__ = ["{name}"]',
            },
            "README.md": {
                "Plugin Name": name,
                "Your Name": author,
            },
        }

        # 应用替换
        for file, file_replacements in replacements.items():
            file_path = os.path.join(plugin_dir, file)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # 应用所有替换
                for old_str, new_str in file_replacements.items():
                    content = content.replace(old_str, new_str)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

        print(success(f"插件模板 '{command(name)}' 创建成功!"))
        print(info(f"插件目录: {plugin_dir}"))
        print(info("请修改插件信息并添加功能代码。"))

    except Exception as e:
        print(error(f"创建插件模板时出错: {e}"))
        # 如果出错，清理已创建的目录
        if os.path.exists(plugin_dir):
            try:
                shutil.rmtree(plugin_dir)
            except:
                pass


@registry.register(
    "remove",
    "卸载插件",
    "remove <插件名>",
    aliases=["r", "uninstall"],
    category="plg",
    show_in_help=False,
)
def remove_plugin(plugin: str) -> None:
    """Remove a plugin."""
    plugins = list_plugins(False)
    if plugins.get(plugin, PLUGIN_BROKEN_MARK) == PLUGIN_BROKEN_MARK:
        print(error(f"插件 {command(plugin)} 不存在!"))
        return

    shutil.rmtree(f"{config.plugin.plugins_dir}/{plugin}")
    print(success(f"插件 {command(plugin)} 卸载成功!"))


@registry.register(
    "list",
    "列出已安装插件",
    "list",
    aliases=["l", "ls"],
    category="plg",
    show_in_help=False,
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
            # 计算字符显示宽度的函数 - 中文字符占用两个宽度单位
            def get_display_width(s):
                width = 0
                for char in s:
                    if "\u4e00" <= char <= "\u9fff":
                        width += 2
                    else:
                        width += 1
                return width

            # 计算最大显示宽度
            max_dir_width = max(get_display_width(dir) for dir in plugins.keys())

            # 设置列宽并添加适当间距
            dir_column_width = max(max_dir_width, 8) + 2

            # 打印表头
            dir_text = "插件目录"
            version_text = "版本"

            dir_text_width = get_display_width(dir_text)

            # 创建对齐的表头 - 颜色代码不占用终端空间
            dir_header = header(dir_text) + " " * (dir_column_width - dir_text_width)

            print(f"{dir_header}  {header(version_text)}")

            # 分隔线
            separator_width = dir_column_width + 30
            print("─" * separator_width)

            for dir, version in plugins.items():
                status = success if version != PLUGIN_BROKEN_MARK else error

                # 计算实际显示宽度
                dir_width = get_display_width(dir)

                # 计算所需填充 - 颜色代码不占用终端空间
                dir_padding = dir_column_width - dir_width

                # 格式化输出
                dir_col = command(dir) + " " * dir_padding
                print(f"{dir_col}  {status(version)}")
        else:
            print(warning("没有安装任何插件!\n\n"))
    return plugins


@registry.register(
    "list_remote",
    "列出远程可用插件",
    "list_remote",
    aliases=["lr"],
    category="plg",
    show_in_help=True,
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
            print(warning("没有找到可用的插件"))
            return

        # 计算字符显示宽度的函数 - 中文字符占用两个宽度单位
        def get_display_width(s):
            width = 0
            for char in s:
                if "\u4e00" <= char <= "\u9fff":
                    width += 2
                else:
                    width += 1
            return width

        # 计算最大显示宽度
        max_name_width = max(get_display_width(name) for name in plugins.keys())
        max_author_width = max(
            get_display_width(plugin.get("author", "Unknown"))
            for plugin in plugins.values()
        )

        # 确保最小宽度并添加适当间距
        name_column_width = max(max_name_width, 8) + 2
        author_column_width = max(max_author_width, 8) + 2

        # 打印表头
        name_text = "插件名"
        author_text = "作者"
        desc_text = "描述"

        name_text_width = get_display_width(name_text)
        author_text_width = get_display_width(author_text)

        # 创建对齐的表头 - 颜色代码不占用终端空间
        name_header = header(name_text) + " " * (name_column_width - name_text_width)
        author_header = header(author_text) + " " * (
            author_column_width - author_text_width
        )

        print(f"{name_header}  {author_header}  {header(desc_text)}")

        # 分隔线
        separator_width = name_column_width + author_column_width + 40
        print("─" * separator_width)

        # 打印每个插件的信息
        for name, plugin in sorted(plugins.items()):
            author = plugin.get("author", "Unknown")
            description = plugin.get("description", "无描述")

            # 计算实际显示宽度
            name_width = get_display_width(name)
            author_width = get_display_width(author)

            # 计算所需填充 - 颜色代码不占用终端空间
            name_padding = name_column_width - name_width
            author_padding = author_column_width - author_width

            # 格式化输出
            name_col = command(name) + " " * name_padding
            author_col = info(author) + " " * author_padding

            print(f"{name_col}  {author_col}  {description}")

    except Exception as e:
        print(error(f"获取插件列表时出错: {e}"))
