"""System management commands for NcatBot CLI."""

import subprocess
import sys
import time

from ncatbot.adapter.nc.install import install_napcat
from ncatbot.cli.registry import registry
from ncatbot.cli.utils import (
    NUMBER_SAVE,
    PYPI_SOURCE,
)
from ncatbot.core import BotClient
from ncatbot.utils import config


@registry.register("setqq", "重新设置 QQ 号", "setqq", aliases=["qq"])
def set_qq() -> str:
    """Set or update the QQ number."""
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
    """Start the NcatBot client."""
    from ncatbot.cli.utils import LOG, get_qq

    print("正在启动 NcatBot...")
    print("按下 Ctrl + C 可以正常退出程序")
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
    """Update NcatBot and NapCat."""
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


@registry.register("exit", "退出 CLI 工具", "exit", aliases=["quit", "q"])
def exit_cli() -> None:
    """Exit the CLI tool."""
    print("\n 正在退出 Ncatbot CLI. 再见!")
