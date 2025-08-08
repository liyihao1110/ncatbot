"""Main entry point for NcatBot CLI."""

import argparse
import os
import sys
from typing import Optional

from ncatbot.cli.commands.config_commands import set_qq
from ncatbot.cli.commands.info_commands import show_meta
from ncatbot.cli.commands.registry import registry
from ncatbot.cli.utils import CLIExit
from ncatbot.cli.utils.colors import error, header, info, success, title, warning
from ncatbot.utils import get_log
from ncatbot.utils import ncatbot_config as config

logger = get_log("CLI")


def setup_work_directory(work_dir: Optional[str] = None) -> None:
    """Set up the working directory for NcatBot."""
    if work_dir is None:
        work_dir = os.getcwd()

    if not os.path.exists(work_dir):
        raise FileNotFoundError(f"工作目录 {work_dir} 不存在")

    os.chdir(work_dir)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="NcatBot CLI")
    parser.add_argument("-c", "--command", help="要执行的命令")
    parser.add_argument("-a", "--args", nargs="*", help="命令参数", default=[])
    parser.add_argument("-w", "--work-dir", help="工作目录")
    parser.add_argument("-d", "--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    return parser.parse_args()


def handle_command_mode(args: argparse.Namespace) -> None:
    """Handle command line mode."""
    from ncatbot.utils.logger import logging

    if args.command not in ["run", "start", "r"]:  # 有些时候日志很烦
        logging.getLogger().setLevel(logging.WARNING)

    try:
        registry.execute(args.command, *args.args)
    except Exception as e:
        logger.error(f"执行命令时出错: {e}")
        print(error(f"执行命令时出错: {e}"))
        sys.exit(1)


def handle_interactive_mode() -> None:
    """Handle interactive mode."""
    print(header("输入 help 查看帮助"))
    print(header("输入 s 启动 NcatBot, 输入 q 退出 CLI"))
    while True:
        try:
            cmd = input(f"{info('NcatBot')} ({success(config.bt_uin)})> ").strip()
            if not cmd:
                continue

            parts = cmd.split()
            cmd_name = parts[0]
            cmd_args = parts[1:]

            registry.execute(cmd_name, *cmd_args)
        except KeyboardInterrupt:
            print("\n" + info("再见!"))
            break
        except CLIExit:
            break
        except Exception as e:
            logger.error(f"执行命令时出错: {e}")
            print(error(f"执行命令时出错: {e}"))


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()

    # Show version and exit if requested
    if args.version:
        show_meta()
        return

    try:
        setup_work_directory(args.work_dir)
    except FileNotFoundError as e:
        logger.error(e)
        print(error(str(e)))
        sys.exit(1)

    # Check if QQ number is set to default value and prompt for setting it
    if config.bt_uin == config._default_bt_uin:
        print(warning("检测到 QQ 号未设置，请先设置 QQ 号"))
        set_qq()

    if args.command is not None:
        handle_command_mode(args)
    else:
        print(title("\n欢迎使用 NcatBot CLI!"))
        handle_interactive_mode()


if __name__ == "__main__":
    main()
