import os
import shutil
import subprocess
import sys

import requests

from ncatbot.core import BotClient
from ncatbot.plugin.loader import get_pulgin_info_by_name
from ncatbot.utils.config import config
from ncatbot.utils.io import download_file

# TODO: 解决插件依赖安装问题

PYPI_SOURCE = "http://mirrors.aliyun.com/pypi/simple/"
GITHUB_PROXY = "https://ghfast.top/"
NCATBOT_PATH = "ncatbot"
NUMBER_SAVE = "number.txt"
PLUGIN_DOWNLOAD_REPO = (
    "https://raw.githubusercontent.com/ncatbot/NcatBot-Plugins/refs/heads/main/plugins"
)


def gen_plugin_version_url(plugin):
    return f"{GITHUB_PROXY}/{PLUGIN_DOWNLOAD_REPO}/{plugin}/version.txt"


def gen_plugin_download_url(plugin, version):
    return f"{GITHUB_PROXY}/{PLUGIN_DOWNLOAD_REPO}/{plugin}/{version}.zip"


def get_qq():
    if os.path.exists(NUMBER_SAVE):
        with open(NUMBER_SAVE, "r") as f:
            return f.read()
    return set_qq()


def set_qq():
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


def install(plugin):
    def get_versions():
        response = requests.get(version_url)
        if response.status_code != 200:
            print(f"获取版本信息失败: {response.status_code}")
            return False, []
        return True, response.content.decode("utf-8").split("\n")

    def install_plugin(version):
        print("正在下载插件包...")
        download_file(gen_plugin_download_url(plugin, version), f"plugins/{plugin}.zip")
        print("正在解压插件包...")
        shutil.unpack_archive(f"plugins/{plugin}.zip", "plugins/")
        print("正在安装插件第三方依赖...")
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                f"plugins/{plugin}/requirements.txt",
                "-i",
                PYPI_SOURCE,
            ],
            shell=True,
        )
        process.wait()

    os.makedirs("plugins", exist_ok=True)
    print(f"正在尝试安装插件: {plugin}")
    version_url = gen_plugin_version_url(plugin)
    status, versions = get_versions()
    if not status:
        return False

    latest_version = versions[-1]
    exist, current_version = get_pulgin_info_by_name(plugin)
    if exist:
        if current_version == latest_version:
            print(f"插件 {plugin} 已经是最新版本: {current_version}")
            return
        print(
            f"插件 {plugin} 已经安装, 当前版本: {current_version}, 最新版本: {latest_version}"
        )
        if input(f"是否更新插件 {plugin} (y/n): ").lower() not in ["y", "yes"]:
            return
        shutil.rmtree(f"plugins/{plugin}")
    install_plugin(latest_version)
    print(f"插件 {plugin}-{latest_version} 安装成功!")


def start():
    print("正在启动 NcatBot...")
    print("按下 Ctrl + C 可以正常退出程序")
    config.set_bot_uin(get_qq())
    client = BotClient()
    client.run()


def update():
    print("正在更新 Ncatbot 版本...")
    process = subprocess.Popen(
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
    )
    process.wait()
    print("Ncatbot 版本更新成功!")


def help(qq):
    print("欢迎使用 NcatBot CLI!")
    print(f"当前 QQ 号为: {qq}")
    print("支持的命令:")
    print("1. 'install <插件名>' - 安装插件")
    print("2. 'setqq' - 重新设置 QQ 号")
    print("3. 'start' - 启动 NcatBot")
    print("4. 'update' - 更新 NcatBot")
    print("5. 'exit' - 退出 CLI 工具")


def main():
    os.chdir(NCATBOT_PATH)
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
                start()
            elif command == "update":
                update()
            elif command == "exit":
                print("\n 正在退出 Ncatbot CLI. 再见!")
            else:
                print(f"不支持的命令: {command}")
        except KeyboardInterrupt:
            print("\n 正在退出 Ncatbot CLI. 再见!")
            break
        except Exception as e:
            print(f"出现错误: {e}")


main()
