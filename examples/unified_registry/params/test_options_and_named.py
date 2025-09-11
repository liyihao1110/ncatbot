import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

from .plugins.params_options_plugin import ParamsOptionsPlugin


async def run_options_and_named_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(ParamsOptionsPlugin)

    # 短选项
    await helper.send_private_message("/list")
    helper.assert_reply_sent("列出目录: .")
    helper.clear_history()

    await helper.send_private_message("/list -l")
    helper.assert_reply_sent("列出目录: . (长格式)")
    helper.clear_history()

    await helper.send_private_message("/list -la")
    helper.assert_reply_sent("列出目录: . (长格式, 显示隐藏)")
    helper.clear_history()

    await helper.send_private_message("/list -lah /home")
    helper.assert_reply_sent("列出目录: /home (长格式, 显示隐藏, 人类可读)")
    helper.clear_history()

    # 长选项
    await helper.send_private_message("/backup /data")
    helper.assert_reply_sent("备份 /data")
    helper.clear_history()

    await helper.send_private_message("/backup /data --compress")
    helper.assert_reply_sent("备份 /data [压缩]")
    helper.clear_history()

    await helper.send_private_message("/backup /data --compress --encrypt")
    helper.assert_reply_sent("备份 /data [压缩, 加密]")
    helper.clear_history()

    # 参数赋值
    await helper.send_private_message("/deploy myapp")
    helper.assert_reply_sent("部署 myapp: 环境=dev, 端口=8080, 进程=4")
    helper.clear_history()

    await helper.send_private_message("/deploy myapp --env=prod")
    helper.assert_reply_sent("部署 myapp: 环境=prod, 端口=8080, 进程=4")
    helper.clear_history()

    await helper.send_private_message("/deploy myapp --env=prod --port=9000 --workers=8")
    helper.assert_reply_sent("部署 myapp: 环境=prod, 端口=9000, 进程=8")
    helper.clear_history()

    # 复杂组合语法
    await helper.send_private_message("/process data.csv")
    helper.assert_reply_sent("处理文件: data.csv → result.txt (json格式)")
    helper.clear_history()

    await helper.send_private_message("/process data.csv -v --output=output.xml --format=xml")
    helper.assert_reply_sent("处理文件: data.csv → output.xml (xml格式) [详细模式]")
    helper.clear_history()

    await helper.send_private_message('/process "my file.txt" --force -v')
    helper.assert_reply_sent("处理文件: my file.txt → result.txt (json格式) [详细模式] [强制模式]")
    helper.clear_history()

    # 选项组
    await helper.send_private_message("/export users")
    helper.assert_reply_sent("导出 users 数据为 json 格式")
    helper.clear_history()

    await helper.send_private_message("/export users --csv")
    helper.assert_reply_sent("导出 users 数据为 csv 格式")
    helper.clear_history()

    await helper.send_private_message("/export users --xml")
    helper.assert_reply_sent("导出 users 数据为 xml 格式")
    helper.clear_history()

    print("\n✅ options_and_named 测试通过")


if __name__ == "__main__":
    asyncio.run(run_options_and_named_tests())


