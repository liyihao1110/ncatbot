"""Main entry point for NcatBot CLI."""

import argparse
import os
from typing import Optional


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
    return parser.parse_args()


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()
    setup_work_directory(args.work_dir)

    if args.command is not None:
        # Command line mode
        from ncatbot.utils.logger import logging

        if args.command not in ["run", "start", "r"]:  # 有些时候日志很烦
            logging.getLogger().setLevel(logging.WARNING)

        from ncatbot.cli import registry

        try:
            registry.execute(args.command, *args.args)
        except Exception as e:
            raise e
    else:
        # Interactive mode
        from ncatbot.cli import get_qq, registry, system_commands

        print("输入 help 查看帮助")
        print("输入 s 启动 NcatBot, 输入 q 退出 CLI")
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
                    return

                registry.execute(cmd_name, *cmd_args)
            except KeyboardInterrupt:
                print("\n再见!")
                break
            except Exception as e:
                print(f"错误: {e}")


if __name__ == "__main__":
    main()
