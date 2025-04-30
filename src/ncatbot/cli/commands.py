"""Plugin management commands for NcatBot CLI."""

import os
import shutil
import subprocess
import sys
import time
from typing import Any, Callable, Dict, List, Optional

from ncatbot.cli.registry import registry
from ncatbot.cli.utils import (
    LOG,
    NUMBER_SAVE,
    PLUGIN_BROKEN_MARK,
    PYPI_SOURCE,
    BotClient,
    config,
    get_log,
    get_plugin_info_by_name,
    get_proxy_url,
    install_plugin_dependencies,
)

try:
    from ncatbot.adapter.nc.install import install_napcat
    from ncatbot.core import BotClient
    from ncatbot.plugin import install_plugin_dependencies
    from ncatbot.scripts import get_plugin_info_by_name
    from ncatbot.utils import PLUGIN_BROKEN_MARK, config, get_log, get_proxy_url
except ImportError:
    # For development without ncatbot installed
    print("警告: ncatbot 模块未安装，部分功能可能无法使用")
    # install_napcat = lambda *args: None
    # BotClient = object
    # install_plugin_dependencies = lambda *args: None
    # get_plugin_info_by_name = lambda *args: (True, "0.0.1")
    # PLUGIN_BROKEN_MARK = "BROKEN"
    # config = type("Config", (), {"set_bot_uin": lambda *args: None})()
    # get_log = lambda *args: type("Logger", (), {"error": print})()
    # get_proxy_url = lambda: "https://ghproxy.com"


class Command:
    """Command class to represent a CLI command"""

    def __init__(
        self,
        name: str,
        func: Callable,
        description: str,
        usage: str,
        help_text: Optional[str] = None,
        aliases: Optional[List[str]] = None,
    ):
        self.name = name
        self.func = func
        self.description = description
        self.usage = usage
        self.help_text = help_text or description
        self.aliases = aliases or []


class CommandRegistry:
    """Registry for CLI commands"""

    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.aliases: Dict[str, str] = {}

    def register(
        self,
        name: str,
        description: str,
        usage: str,
        help_text: Optional[str] = None,
        aliases: Optional[List[str]] = None,
    ):
        """Decorator to register a command"""

        def decorator(func: Callable) -> Callable:
            cmd = Command(name, func, description, usage, help_text, aliases)
            self.commands[name] = cmd

            # Register aliases
            if aliases:
                for alias in aliases:
                    self.aliases[alias] = name

            return func

        return decorator

    def execute(self, command_name: str, *args, **kwargs) -> Any:
        """Execute a command by name"""
        # Check if the command is an alias
        if command_name in self.aliases:
            command_name = self.aliases[command_name]

        if command_name not in self.commands:
            print(f"不支持的命令: {command_name}")
            return None

        return self.commands[command_name].func(*args, **kwargs)

    def get_help(self) -> str:
        """Generate help text for all commands"""
        help_lines = ["支持的命令:"]
        for i, (name, cmd) in enumerate(sorted(self.commands.items()), 1):
            # Include aliases in the help text if they exist
            alias_text = f" (别名: {', '.join(cmd.aliases)})" if cmd.aliases else ""
            help_lines.append(f"{i}. '{cmd.usage}' - {cmd.description}{alias_text}")
        return "\n".join(help_lines)


@registry.register("setqq", "重新设置 QQ 号", "setqq", aliases=["qq"])
def set_qq() -> str:
    # 提示输入, 确认输入, 保存到文件
    qq = input("请输入 QQ 号: ")
    if not qq.isdigit():
        print("QQ 号必须为数字!")
        return set_qq()

    qq_confirm = input(f"请再输入一遍 QQ 号 {qq} 并确认: ")
    if qq != qq_confirm:
        print("两次输入的 QQ 号不一致!")
        return set_qq()

    with open(NUMBER_SAVE, "w") as f:
        f.write(qq)
    return qq


@registry.register(
    "start", "启动 NcatBot", "start [-d|-D|--debug]", aliases=["s", "run"]
)
def start(*args: str) -> None:
    print("正在启动 NcatBot...")
    print("按下 Ctrl + C 可以正常退出程序")
    from ncatbot.cli.utils import get_qq

    config.set_bot_uin(get_qq())
    try:
        client = BotClient()
        client.run(
            skip_ncatbot_install_check=(
                "-d" in args or "-D" in args or "--debug" in args
            )
        )
        # skip_ncatbot_install_check 是 NcatBot 本体开发者调试后门
    except Exception as e:
        LOG.error(e)


@registry.register(
    "update", "更新 NcatBot 和 NapCat", "update", aliases=["u", "upgrade"]
)
def update() -> None:
    print("正在更新 NapCat 版本")
    install_napcat("update")
    print("正在更新 Ncatbot 版本, 更新后请重新运行 NcatBotCLI 或者 main.exe")
    time.sleep(1)
    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "ncatbot",
            "-i",
            PYPI_SOURCE,
        ],
        shell=True,
        start_new_session=True,
    )
    print("Ncatbot 正在更新...")
    time.sleep(10)
    print("更新成功, 请重新运行 NcatBotCLI 或者 main.exe")
    exit(0)


@registry.register("remove", "卸载插件", "remove <插件名>", aliases=["r", "uninstall"])
def remove_plugin(plugin: str) -> None:
    plugins = list_plugin(False)
    if plugins.get(plugin, PLUGIN_BROKEN_MARK) == PLUGIN_BROKEN_MARK:
        print(f"插件 {plugin} 不存在!")

    shutil.rmtree(f"plugins/{plugin}")
    print(f"插件 {plugin} 卸载成功!")


@registry.register("list", "列出已安装插件", "list", aliases=["l", "ls"])
def list_plugin(enable_print: bool = True) -> Dict[str, str]:
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


@registry.register("exit", "退出 CLI 工具", "exit", aliases=["quit", "q"])
def exit_cli() -> None:
    print("\n 正在退出 Ncatbot CLI. 再见!")
    sys.exit(0)


@registry.register("help", "显示命令帮助信息", "help [命令名]", aliases=["h", "?"])
def show_command_help(command_name: Optional[str] = None) -> None:
    """Show detailed help for a specific command or all commands"""
    if command_name is None:
        # Show general help
        from ncatbot.cli.utils import get_qq

        qq = get_qq()
        show_help(qq)
        return

    # Show help for a specific command
    if command_name not in registry.commands:
        print(f"不支持的命令: {command_name}")
        return

    cmd = registry.commands[command_name]
    print(f"命令: {cmd.name}")
    print(f"用法: {cmd.usage}")
    print(f"描述: {cmd.description}")
    if cmd.help_text and cmd.help_text != cmd.description:
        print(f"详细说明: {cmd.help_text}")


@registry.register("version", "显示 NcatBot 版本", "version", aliases=["v", "ver"])
def show_version() -> None:
    """Show the version of NcatBot"""
    try:
        import pkg_resources

        version = pkg_resources.get_distribution("ncatbot").version
        print(f"NcatBot 版本: {version}")
    except (ImportError, pkg_resources.DistributionNotFound):
        print("无法获取 NcatBot 版本信息")


@registry.register(
    "create", "创建插件模板", "create <插件名>", aliases=["new", "template"]
)
def create_plugin_template(plugin_name: str) -> None:
    """Create a new plugin template with the given name"""
    import os
    import re

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
        import shutil

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
from ncatbot.core import BaseMessage, GroupMessage, PrivateMessage

bot = CompatibleEnrollment  # 兼容回调函数注册器


class {plugin_name}(BasePlugin):
    name = "{plugin_name}"  # 插件名称
    version = "0.0.1"  # 插件版本

    @bot.group_event()
    async def on_group_event(self, msg: GroupMessage):
        # 群消息事件处理
        if msg.raw_message == "测试":
            await self.api.post_group_msg(msg.group_id, text="{plugin_name} 插件测试成功喵")

    @bot.private_event()
    async def on_private_event(self, msg: PrivateMessage):
        # 好友消息事件处理
        if msg.raw_message == "测试":
            await self.api.post_friend_msg(msg.user_id, text="{plugin_name} 插件测试成功喵")

    async def on_load(self):
        # 插件加载时执行的操作
        print(f"{{self.name}} 插件已加载")
        print(f"插件版本: {{self.version}}")
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

## 使用方法

1. 在群聊中发送 "测试" 消息
2. 在私聊中发送 "测试" 消息

## 配置项

暂无配置项。

## 依赖

- NcatBot

## 作者

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


def show_help(qq: str) -> None:
    print("欢迎使用 NcatBot CLI!")
    print(f"当前 QQ 号为: {qq}")
    print(registry.get_help())
