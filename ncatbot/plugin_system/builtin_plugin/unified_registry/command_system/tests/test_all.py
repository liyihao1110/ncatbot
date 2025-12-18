"""运行所有测试

这个文件提供了一个统一的入口来运行所有的命令系统测试
"""

import sys
import traceback


def run_all_tests():
    """运行所有测试"""
    test_modules = [
        ("字符串分词器", "test_string_tokenizer"),
        ("高级命令解析器", "test_advanced_parser"),
        ("消息级别分词器", "test_message_tokenizer"),
        ("集成测试", "test_integration"),
    ]

    results = {}

    for test_name, module_name in test_modules:
        print(f"\n{'=' * 50}")
        print(f"运行 {test_name} 测试...")
        print("=" * 50)

        try:
            # 动态导入并运行测试模块
            module = __import__(
                f"ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.tests.{module_name}",
                fromlist=[""],
            )

            # 运行测试主函数
            if hasattr(module, "__main__"):
                exec(
                    open(
                        f"ncatbot/plugin_system/builtin_plugin/unified_registry/command_system/tests/{module_name}.py"
                    ).read()
                )

            results[test_name] = "✓ 通过"
            print(f"\n{test_name} 测试完成！")

        except Exception as e:
            results[test_name] = f"✗ 失败: {str(e)}"
            print(f"\n{test_name} 测试失败:")
            print(traceback.format_exc())

    # 总结结果
    print(f"\n{'=' * 60}")
    print("测试总结")
    print("=" * 60)

    all_passed = True
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
        if "✗" in result:
            all_passed = False

    print(f"\n总体结果: {'✅ 所有测试通过' if all_passed else '❌ 部分测试失败'}")

    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
