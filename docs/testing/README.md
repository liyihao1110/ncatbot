# NcatBot 测试文档

欢迎使用 NcatBot 测试框架！本文档将帮助您了解如何为 NcatBot 插件编写高质量的测试。

## 📚 文档目录

### [快速上手指南](./quick-start.md)
100 行代码让您快速了解 NcatBot 测试框架的基本用法，包含一个完整的测试示例。

### [完整测试指南](./guide.md)
深入了解测试框架的所有功能，包括：
- 核心组件详解（TestClient、TestHelper、EventFactory、MockAPIAdapter）
- 高级测试用法
- 调试技巧

### [标准化测试最佳实践](./best-practice-unittest.md)
使用 Python unittest 框架编写规范的测试：
- 基础测试类设置
- 高级测试模式（Mock、参数化测试）
- 测试套件组织
- 持续集成配置

### [简单函数式测试最佳实践](./best-practice-simple.md)
快速编写测试函数，适合：
- 快速验证和调试
- 原型开发
- 交互式测试
- 性能测试

### [API 参考文档](./api-reference.md)
所有测试相关类和方法的详细参考，包含参数说明和使用示例。

## 🚀 快速开始

```python
from ncatbot.utils.testing import TestClient, TestHelper
from my_plugin import MyPlugin
import asyncio

async def test_my_plugin():
    # 创建测试环境
    client = TestClient()
    helper = TestHelper(client)
    
    # 启动客户端并注册插件
    client.start()
    client.register_plugin(MyPlugin)
    
    # 发送测试消息
    await helper.send_private_message("/hello")
    
    # 验证回复
    reply = helper.get_latest_reply()
    assert reply is not None
    print("✅ 测试通过！")

asyncio.run(test_my_plugin())
```

## 🎯 选择合适的测试方法

### 使用标准化测试（unittest）当您需要：
- ✅ 持续集成和自动化测试
- ✅ 测试覆盖率报告
- ✅ 团队协作的大型项目
- ✅ 复杂的测试场景和断言

### 使用简单函数式测试当您需要：
- ✅ 快速验证新功能
- ✅ 调试具体问题
- ✅ 编写演示和文档示例
- ✅ 一次性测试脚本

## 💡 测试框架特性

- **Mock 模式**: 无需真实 QQ 客户端即可测试
- **插件隔离**: 按需加载测试所需的插件
- **API 模拟**: 完整的 API 调用拦截和模拟
- **事件工厂**: 轻松创建各种测试事件
- **丰富的断言**: 专为 QQ 机器人测试设计的断言方法

## 📢 测试框架注意事项

- 一次运行中，**插件加载后无法卸载**，必须仅在测试的最开始可以加载必要的插件。

## 📖 相关资源

- [NcatBot 主文档](../../README.md)
- [插件开发指南](../plugin-development/README.md)
- [API 文档](../api/README.md)

## 🤝 贡献

如果您在使用测试框架时遇到问题或有改进建议，欢迎：
- 提交 Issue
- 提交 Pull Request
- 参与讨论

祝您测试愉快！🎉
