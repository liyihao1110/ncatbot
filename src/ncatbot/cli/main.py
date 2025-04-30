"""Main entry point for NcatBot CLI."""

import argparse
import os
import sys
from typing import Optional

from . import system_commands
from .registry import registry
from .utils import NCATBOT_PATH, get_qq


def setup_work_directory(work_dir: Optional[str] = None) -> None:
    """Set up the working directory for NcatBot."""
    if work_dir is None:
        work_dir = os.getcwd()

    if not os.path.exists(work_dir):
        print(f"工作目录 {work_dir} 不存在")
        sys.exit(1)

    os.chdir(work_dir)
    if not os.path.exists(NCATBOT_PATH):
        os.makedirs(NCATBOT_PATH)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="NcatBot CLI")
    parser.add_argument("-c", "--command", help="要执行的命令")
    parser.add_argument("-a", "--args", nargs="*", help="命令参数", default=[])
    parser.add_argument("-w", "--work-dir", help="工作目录")
    parser.add_argument("-d", "--debug", action="store_true", help="启用调试模式")
    return parser.parse_args()


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()
    setup_work_directory(args.work_dir)

    if args.command is None:
        # Interactive mode
        while True:
            try:
                cmd = input(f"NcatBot ({get_qq()})> ").strip()
                if not cmd:
                    continue

                parts = cmd.split()
                cmd_name = parts[0]
                cmd_args = parts[1:]

                if cmd_name == "exit":
                    system_commands.exit_cli()
                    break

                registry.execute(cmd_name, *cmd_args)
            except KeyboardInterrupt:
                print("\n再见!")
                break
            except Exception as e:
                print(f"错误: {e}")
    else:
        # Command line mode
        try:
            registry.execute(args.command, *args.args)
        except Exception as e:
            print(f"错误: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
