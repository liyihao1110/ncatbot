"""Sentence 类型功能测试模块"""


def test_sentence_feature():
    """测试 Sentence 类型功能的单元测试
    
    直接运行此函数来验证 Sentence 类型是否正确实现
    
    Returns:
        bool: 测试是否通过
    """
    print("🧪 开始测试 Sentence 类型功能...")
    
    # 导入必要的模块
    from ncatbot.core.event.message_segment.sentence import Sentence
    from ncatbot.core.event.message_segment import Text, MessageArray
    from ncatbot.core.event import BaseMessageEvent
    from ncatbot.plugin_system.builtin_plugin.filter_registry.analyzer.func_analyzer import FuncAnalyser
    from unittest.mock import Mock
    import inspect
    
    # 测试 1: Sentence 类型基本功能
    print("\n1️⃣ 测试 Sentence 基本功能")
    try:
        s = Sentence("Hello World Test")
        assert str(s) == "Hello World Test"
        assert isinstance(s, str)  # 继承自 str
        assert s.upper() == "HELLO WORLD TEST"  # 支持 str 方法
        assert s.split() == ["Hello", "World", "Test"]  # 支持 str 方法
        assert len(s) == 16
        print("  ✅ Sentence 基本功能正常")
    except Exception as e:
        print(f"  ❌ Sentence 基本功能测试失败: {e}")
        return False
    
    # 测试 2: FuncAnalyser.detect_args_type() 支持 Sentence
    print("\n2️⃣ 测试 detect_args_type 支持 Sentence")
    try:
        # 创建模拟函数
        def mock_func(self, event: BaseMessageEvent, content: Sentence):
            pass
        
        analyzer = FuncAnalyser(mock_func)
        arg_types = analyzer.detect_args_type()
        assert arg_types == [Sentence]
        print("  ✅ detect_args_type 正确识别 Sentence 类型")
    except Exception as e:
        print(f"  ❌ detect_args_type 测试失败: {e}")
        return False
    
    # 测试 3: 参数转换 - Sentence vs str 行为对比
    print("\n3️⃣ 测试参数转换行为对比")
    
    # 创建模拟事件
    def create_mock_event(text: str):
        event = Mock(spec=BaseMessageEvent)
        text_segment = Text(text=text)
        event.message = MessageArray()
        event.message.messages = [text_segment]
        return event
    
    try:
        # 测试 str 类型（应该失败，因为消息有3个单词但函数只接受1个参数）
        def str_func(self, event: BaseMessageEvent, word: str):
            pass
        
        str_analyzer = FuncAnalyser(str_func)
        str_event = create_mock_event("Hello World Test")
        str_success, str_args = str_analyzer.convert_args(str_event)
        
        assert str_success == False  # 应该失败：3个单词但只有1个str参数
        print("  ✅ str 类型正确失败（参数个数不匹配：3个单词vs1个参数）")
        
        # 测试 Sentence 类型（应该取完整文本）
        def sentence_func(self, event: BaseMessageEvent, content: Sentence):
            pass
        
        sentence_analyzer = FuncAnalyser(sentence_func)
        sentence_event = create_mock_event("Hello World Test")
        sentence_success, sentence_args = sentence_analyzer.convert_args(sentence_event)
        
        assert sentence_success == True
        assert len(sentence_args) == 1
        assert str(sentence_args[0]) == "Hello World Test"  # 完整文本
        assert isinstance(sentence_args[0], Sentence)  # 类型正确
        print("  ✅ Sentence 类型正确解析（完整文本）")
        
    except Exception as e:
        print(f"  ❌ 参数转换测试失败: {e}")
        return False
    
    # 测试 4: 混合参数类型
    print("\n4️⃣ 测试混合参数类型")
    try:
        def mixed_func(self, event: BaseMessageEvent, cmd: str, content: Sentence):
            pass
        
        mixed_analyzer = FuncAnalyser(mixed_func)
        mixed_event = create_mock_event("test Hello World")
        mixed_success, mixed_args = mixed_analyzer.convert_args(mixed_event)
        
        assert mixed_success == True
        assert len(mixed_args) == 2
        assert mixed_args[0] == "test"  # str 类型，第一个单词
        assert str(mixed_args[1]) == "Hello World"  # Sentence 类型，剩余文本
        assert isinstance(mixed_args[1], Sentence)
        print("  ✅ 混合参数类型正确解析")
        
    except Exception as e:
        print(f"  ❌ 混合参数测试失败: {e}")
        return False
    
    # 测试 5: Text 部分匹配后剩余部分给 Sentence
    print("\n5️⃣ 测试 Text 部分匹配场景")
    try:
        # 场景1: ignore + Sentence
        def ignore_sentence_func(self, event: BaseMessageEvent, content: Sentence):
            pass
        
        analyzer1 = FuncAnalyser(ignore_sentence_func, ignore=["echo"])
        event1 = create_mock_event("echo Hello World Test")
        success1, args1 = analyzer1.convert_args(event1)
        
        assert success1 == True
        assert len(args1) == 1
        assert str(args1[0]) == "Hello World Test"
        assert isinstance(args1[0], Sentence)
        print("  ✅ ignore + Sentence 场景正确")
        
        # 场景2: str + Sentence
        def str_sentence_func(self, event: BaseMessageEvent, cmd: str, content: Sentence):
            pass
        
        analyzer2 = FuncAnalyser(str_sentence_func, ignore=["process"])
        event2 = create_mock_event("process urgent Hello World Test")
        success2, args2 = analyzer2.convert_args(event2)
        
        assert success2 == True
        assert len(args2) == 2
        assert args2[0] == "urgent"
        assert str(args2[1]) == "Hello World Test"
        assert isinstance(args2[1], Sentence)
        print("  ✅ str + Sentence 场景正确")
        
        # 场景3: 多个 str + Sentence
        def multi_str_sentence_func(self, event: BaseMessageEvent, a: str, b: str, content: Sentence):
            pass
        
        analyzer3 = FuncAnalyser(multi_str_sentence_func, ignore=["cmd"])
        event3 = create_mock_event("cmd word1 word2 Hello World Test")
        success3, args3 = analyzer3.convert_args(event3)
        
        assert success3 == True
        assert len(args3) == 3
        assert args3[0] == "word1"
        assert args3[1] == "word2"
        assert str(args3[2]) == "Hello World Test"
        assert isinstance(args3[2], Sentence)
        print("  ✅ 多个 str + Sentence 场景正确")
        
    except Exception as e:
        print(f"  ❌ Text 部分匹配测试失败: {e}")
        return False
    
    print("\n🎉 所有测试通过！Sentence 类型功能正确实现")
    print("\n📋 测试总结:")
    print("  • Sentence 继承自 str，支持所有字符串操作")
    print("  • str 类型参数：按空格分割，只取单个单词")
    print("  • Sentence 类型参数：取完整文本内容（包含空格）")
    print("  • 支持 Text 部分匹配后剩余内容给 Sentence ⭐")
    print("  • 支持 ignore + Sentence、str + Sentence、多参数混合")
    return True


if __name__ == "__main__":
    # 可以直接运行此文件来测试
    test_sentence_feature()
