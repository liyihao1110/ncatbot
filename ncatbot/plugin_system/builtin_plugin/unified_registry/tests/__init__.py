"""unified_registry 模块测试包

这个包包含了对 unified_registry 模块的全面测试，包括：

- 单元测试：测试各个组件的独立功能
- 集成测试：测试组件间的协作
- 工作流测试：测试完整的业务流程

测试结构：
- conftest.py: 全局测试配置和 fixtures
- test_unified_registry_plugin.py: 主插件测试
- filter_system/: 过滤器系统测试
- command_system/: 命令系统测试  
- trigger/: 触发器系统测试
- integration/: 集成测试

运行测试：
    pytest ncatbot/plugin_system/builtin_plugin/unified_registry/tests/
"""
