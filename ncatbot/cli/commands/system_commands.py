"""sys management commands for NcatBot CLI."""

import subprocess
import sys
import time

from ncatbot.cli.commands.registry import registry
from ncatbot.cli.utils import PYPI_SOURCE, CLIExit
from ncatbot.cli.utils.colors import error, header, info, success
from ncatbot.core import BotClient, install_napcat
from ncatbot.utils.logger import get_log

LOG = get_log("CLI")


@registry.register(
    "start",
    "启动 NcatBot",
    "start [-d|-D|--debug]",
    aliases=["s", "run"],
    category="sys",
)
def start(*args: str) -> None:
    """Start the NcatBot client."""
    print(header("正在启动 NcatBot..."))
    print(info("按下 Ctrl + C 可以正常退出程序"))

    try:
        # 创建客户端
        client = BotClient()  # 密码暂时为空
        # 启动客户端（带调试选项）
        client.run()

    except Exception as e:
        LOG.error(f"启动失败: {e}")
        print(error(f"启动失败: {e}"))


@registry.register(
    "update",
    "更新 NcatBot 和 NapCat",
    "update",
    aliases=["u", "upgrade"],
    category="sys",
    show_in_help=False,
)
def update() -> None:
    """Update NcatBot and NapCat."""
    print(header("正在更新 NapCat 版本"))
    install_napcat()

    print(header("正在更新 Ncatbot 版本, 更新后请重新运行 NcatBotCLI 或者 main.exe"))
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

    print(info("Ncatbot 正在更新..."))
    time.sleep(10)
    print(success("更新成功, 请重新运行 NcatBotCLI 或者 main.exe"))
    exit(0)


@registry.register(
    "exit",
    "退出 CLI 工具",
    "exit",
    aliases=["quit", "q"],
    category="sys",
    show_in_help=False,
)
def exit_cli() -> None:
    """Exit the CLI tool."""
    print("\n" + info("正在退出 Ncatbot CLI. 再见!"))
    raise CLIExit()
