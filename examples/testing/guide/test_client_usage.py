"""
TestClient 基本用法测试
来源: docs/testing/guide.md
"""

from ncatbot.utils.testing import TestClient, TestHelper
from ..common.hello_plugin import HelloPlugin
import asyncio


async def main():
    """测试 TestClient 基本用法"""
    # 创建测试客户端
    client = TestClient(load_plugin=False)  # 默认不加载任何插件
    helper = TestHelper(client)

    # 启动客户端（Mock 模式默认开启）
    client.start()

    # 注册需要测试的插件
    client.register_plugin(HelloPlugin)

    # 获取已注册的插件
    plugins = client.get_registered_plugins()
    print(f"已注册插件: {[p.name for p in plugins]}")

    # 测试插件功能
    await helper.send_private_message("/hello")
    reply = helper.get_latest_reply()
    if reply:
        print("✅ 插件功能测试通过")
    else:
        print("❌ 插件功能测试失败")

    # 卸载插件（注意：通过装饰器等注册的命令无法被卸载）
    if plugins:
        plugin_instance = plugins[0]
        client.unregister_plugin(plugin_instance)
        print(f"已卸载插件: {plugin_instance.name}")

    print("✅ TestClient 基本用法测试完成")


if __name__ == "__main__":
    asyncio.run(main())
