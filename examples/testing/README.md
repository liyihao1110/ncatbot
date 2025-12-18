# NcatBot 测试文档代码验证

这个目录包含了从测试文档中提取的所有代码示例，用于验证文档中代码的正确性。

## 目录结构

- `quick_start/` - 快速上手指南中的代码示例
- `guide/` - 完整测试指南中的代码示例
- `simple_tests/` - 简单函数式测试的代码示例
- `unittest_tests/` - 标准化测试（unittest）的代码示例
- `api_examples/` - API参考文档中的代码示例
- `common/` - 通用的辅助代码和插件

## 运行方法

```bash
# 激活虚拟环境
.\.venv\Scripts\activate

# 运行特定示例
python.exe -m examples.testing.unittest_tests.test_calculator_plugin

```

## 验证状态

- ✅ 已验证：代码可以正常运行
- ❌ 需要修复：代码存在问题
- 🔄 待验证：尚未验证
