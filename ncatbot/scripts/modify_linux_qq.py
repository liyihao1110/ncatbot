import os
import subprocess
import json
from ncatbot.utils.logger import get_log

_log = get_log()


def modify_linux_qq():
    target_folder = "/opt/QQ"
    napcat_folder = f"{target_folder}/napcat"
    # 创建目标文件夹
    if not os.path.exists(napcat_folder):
        subprocess.run(["sudo", "mkdir", "-p", napcat_folder])
    # 移动文件
    _log.info("正在移动文件...")
    try:
        subprocess.run(
            ["sudo", "cp", "-r", "-f", "./NapCat/*", napcat_folder], shell=True
        )
        subprocess.run(["sudo", "chmod", "-R", "777", napcat_folder])
        _log.info("移动文件成功")
    except Exception as e:
        _log.error("文件移动失败, 请检查错误。")
        _log.error(f"错误信息: {e}")
        return False
    # 修补文件
    _log.info("正在修补文件...")
    loadnap_content = (
        f"(async () => {{await import('file://{napcat_folder}/napcat.mjs');}})();"
    )
    loadnap_path = f"{target_folder}/resources/app/loadNapCat.js"
    try:
        with open("temp_loadnap.js", "w") as f:
            f.write(loadnap_content)
        subprocess.run(["sudo", "mv", "temp_loadnap.js", loadnap_path])
        _log.info("修补文件成功")
    except Exception as e:
        _log.error("loadNapCat.js文件写入失败, 请检查错误。")
        _log.error(f"错误信息: {e}")
        return False
    # 修改QQ启动配置
    _log.info("正在修改QQ启动配置...")
    package_path = f"{target_folder}/resources/app/package.json"
    try:
        # 读取原始package.json
        with open(package_path, "r") as f:
            package_data = json.load(f)
        # 修改main字段
        package_data["main"] = "./loadNapCat.js"
        # 写入临时文件
        with open("package.json.tmp", "w") as f:
            json.dump(package_data, f, indent=2)
        # 移动到目标位置
        subprocess.run(["sudo", "mv", "package.json.tmp", package_path])
        _log.info("修改QQ启动配置成功")
    except Exception as e:
        _log.error("修改QQ启动配置失败")
        _log.error(f"错误信息: {e}")
        return False
    return True
