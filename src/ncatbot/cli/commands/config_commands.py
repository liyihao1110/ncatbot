from ncatbot.cli.commands.registry import registry
from ncatbot.utils import ncatbot_config as config


@registry.register(
    "setqq",
    "重新设置 QQ 号",
    "setqq",
    aliases=["qq"],
    category="System",
)
def set_qq() -> str:
    """写入配置文件, 永久生效"""
    qq = input("请输入 QQ 号: ")
    if not qq.isdigit():
        print("QQ 号必须为数字!")
        return set_qq()

    qq_confirm = input(f"请再输入一遍 QQ 号 {qq} 并确认: ")
    if qq != qq_confirm:
        print("两次输入的 QQ 号不一致!")
        return set_qq()

    config.save_permanent_config("bt_uin", qq)
    return qq
