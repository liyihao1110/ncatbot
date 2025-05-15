from ncatbot.cli.commands.registry import registry
from ncatbot.cli.utils.colors import command, error, info, success
from ncatbot.utils import ncatbot_config as config


@registry.register(
    "setqq",
    "重新设置 QQ 号",
    "setqq",
    aliases=["qq"],
    category="sys",
    show_in_help=False,
)
def set_qq() -> str:
    """写入配置文件, 永久生效"""
    qq = input(info("请输入 QQ 号: "))
    if not qq.isdigit():
        print(error("QQ 号必须为数字!"))
        return set_qq()

    qq_confirm = input(info(f"请再输入一遍 QQ 号 {command(qq)} 并确认: "))
    if qq != qq_confirm:
        print(error("两次输入的 QQ 号不一致!"))
        return set_qq()

    config.save_permanent_config("bt_uin", qq)
    print(success(f"QQ 号已设置为 {qq}"))
    return qq
