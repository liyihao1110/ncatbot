import argparse
import os
import shutil
import subprocess
import sys
import time

import requests


def setup_work_directory():
    parser = argparse.ArgumentParser(description="NcatBot CLI 参数表")
    parser.add_argument(
        "work_dir",
        type=str,
        nargs="?",
        default="ncatbot",
        help="可选参数, 默认为 NcatBot 安装目录",
    )
    args = parser.parse_args()
    if not os.path.isdir(args.work_dir):
        print("工作目录参数不合法")
        exit(1)
    print("工作目录: ", os.path.abspath(args.work_dir))
    os.chdir(args.work_dir)
    os.environ["LOG_FILE_PATH"] = os.path.join(os.getcwd(), "logs")


setup_work_directory()


from ncatbot.core import BotClient
from ncatbot.plugin import install_plugin_dependecies
from ncatbot.scripts import get_pulgin_info_by_name
from ncatbot.utils import PLUGIN_BROKEN_MARK, config, get_log, get_proxy_url

# TODO: 解决插件依赖安装问题

LOG = get_log("CLI")

GITHUB_PROXY = get_proxy_url()
PYPI_SOURCE = "https://mirrors.aliyun.com/pypi/simple/"
NCATBOT_PATH = "ncatbot"
TEST_PLUGIN = "TestPlugin"
NUMBER_SAVE = "number.txt"
PLUGIN_DOWNLOAD_REPO = (
    "https://raw.githubusercontent.com/ncatbot/NcatBot-Plugins/refs/heads/main/plugins"
)


def gen_plugin_version_url(plugin):
    return f"{GITHUB_PROXY}/{PLUGIN_DOWNLOAD_REPO}/{plugin}/version.txt"


def gen_plugin_download_url(plugin, version):
    return (
        f"{GITHUB_PROXY}/{PLUGIN_DOWNLOAD_REPO}/{plugin}/{plugin}-{version.strip()}.zip"
    )


def get_qq():
    if os.path.exists(NUMBER_SAVE):
        with open(NUMBER_SAVE, "r") as f:
            return f.read()
    print("第一次运行, 即将安装测试插件, 若不需要测试插件, 稍后可以删除...")
    time.sleep(1)
    install("TestPlugin")
    return set_qq()


def set_qq():
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


def install(plugin, *args):
    def get_versions():
        def remove_empty_values(values):
            return [v for v in values if v != ""]

        version_url = gen_plugin_version_url(plugin)
        print(f"正在获取插件版本信息 {version_url}...")

        response = requests.get(version_url)
        if response.status_code != 200:
            print(f"获取版本信息失败: {response.status_code}, 请检查是否存在该插件")
            return False, []
        return True, remove_empty_values(response.content.decode("utf-8").split("\n"))

    def install_plugin(version):
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
        download_file(gen_plugin_download_url(plugin, version), f"plugins/{plugin}.zip")
        print("正在解压插件包...")
        directory_path = f"plugins/{plugin}"
        os.makedirs(directory_path, exist_ok=True)
        shutil.unpack_archive(f"{directory_path}.zip", directory_path)
        os.remove(f"{directory_path}.zip")
        install_plugin_dependecies(plugin)

    fix = args[0] == "--fix" if len(args) else False

    os.makedirs("plugins", exist_ok=True)
    print(f"正在尝试安装插件: {plugin}")
    status, versions = get_versions()
    if not status:
        return False

    latest_version = versions[-1]
    exist, current_version = get_pulgin_info_by_name(plugin)
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
    install_plugin(latest_version)
    print(f"插件 {plugin}-{latest_version} 安装成功!")


def start(*args, **kwargs):
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


def update():
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
    print("Ncatbot 版本更新成功!")
    print("请重新运行 NcatBotCLI 或者 main.exe")
    time.sleep(1)
    exit(0)


def list_plugin(enable_print=True):
    dirs = os.listdir("plugins")
    plugins = {}
    for dir in dirs:
        try:
            version = get_pulgin_info_by_name(dir)[1]
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


def remove_plugin(plugin):
    plugins = list_plugin(False)
    if plugins.get(plugin, PLUGIN_BROKEN_MARK) == PLUGIN_BROKEN_MARK:
        print(f"插件 {plugin} 不存在!")

    shutil.rmtree(f"plugins/{plugin}")
    print(f"插件 {plugin} 卸载成功!")


def help(qq):
    print("欢迎使用 NcatBot CLI!")
    print(f"当前 QQ 号为: {qq}")
    print("支持的命令:")
    print("1. 'install <插件名> [--fix]' - 安装插件")
    print("2. 'setqq' - 重新设置 QQ 号")
    print("3. 'start' - 启动 NcatBot")
    print("4. 'update' - 更新 NcatBot")
    print("5. 'remove <插件名> ' - 卸载插件")
    print("6. 'list' - 列出已安装插件")
    print("7. 'exit' - 退出 CLI 工具")


def main():
    help(get_qq())
    while True:
        try:
            user_input = input("请输入命令: ").strip()
            if not user_input:
                continue

            command_parts = user_input.split()
            if len(command_parts) < 1:
                continue

            command = command_parts[0]
            if command == "install":
                install(*command_parts[1:])
            elif command == "setqq":
                set_qq()
            elif command == "start":
                start(*command_parts[1:])
            elif command == "update":
                update()
            elif command == "remove":
                remove_plugin(*command_parts[1:])
            elif command == "list":
                list_plugin()
            elif command == "exit":
                print("\n 正在退出 Ncatbot CLI. 再见!")
                break
            else:
                print(f"不支持的命令: {command}")
        except KeyboardInterrupt:
            print("\n 正在退出 Ncatbot CLI. 再见!")
            break
        except Exception as e:
            print(f"出现错误: {e}")


main()
