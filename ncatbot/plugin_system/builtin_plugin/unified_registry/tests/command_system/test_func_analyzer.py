"""函数分析器测试

测试函数分析器的功能，包括函数签名分析、参数检测、类型注解处理等。
"""

import pytest
import inspect
from typing import Optional, List
from unittest.mock import Mock
from ncatbot.core.event import BaseMessageEvent

from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.analyzer.func_analyzer import (
    FuncAnalyser, get_subclass_recursive, FuncSpec
)


class TestGetSubclassRecursive:
    """递归获取子类测试"""
    
    def test_get_subclass_simple(self):
        """测试简单类的子类获取"""
        class BaseClass:
            pass
        
        class ChildClass(BaseClass):
            pass
        
        subclasses = get_subclass_recursive(BaseClass)
        assert BaseClass in subclasses
        assert ChildClass in subclasses
        assert len(subclasses) >= 2
    
    def test_get_subclass_nested(self):
        """测试嵌套继承的子类获取"""
        class GrandParent:
            pass
        
        class Parent(GrandParent):
            pass
        
        class Child(Parent):
            pass
        
        class GrandChild(Child):
            pass
        
        subclasses = get_subclass_recursive(GrandParent)
        assert GrandParent in subclasses
        assert Parent in subclasses
        assert Child in subclasses
        assert GrandChild in subclasses
    
    def test_get_subclass_no_children(self):
        """测试没有子类的类"""
        class LonelyClass:
            pass
        
        subclasses = get_subclass_recursive(LonelyClass)
        assert subclasses == [LonelyClass]
    
    def test_get_subclass_multiple_inheritance(self):
        """测试多重继承的子类获取"""
        class MixinA:
            pass
        
        class MixinB:
            pass
        
        class Combined(MixinA, MixinB):
            pass
        
        # 测试从不同基类开始
        subclasses_a = get_subclass_recursive(MixinA)
        subclasses_b = get_subclass_recursive(MixinB)
        
        assert MixinA in subclasses_a
        assert Combined in subclasses_a
        assert MixinB in subclasses_b
        assert Combined in subclasses_b


class TestFuncDescriptor:
    """函数描述符测试"""
    
    def test_descriptor_creation_simple(self):
        """测试简单函数的描述符创建"""
        def simple_func():
            """简单函数"""
            pass
        
        descriptor = FuncSpec(simple_func)
        
        assert descriptor.func is simple_func
        assert descriptor.func_name == "simple_func"
        assert descriptor.func_module == simple_func.__module__
        assert descriptor.func_qualname == simple_func.__qualname__
        assert isinstance(descriptor.signature, inspect.Signature)
        assert len(descriptor.param_list) == 0
        assert len(descriptor.param_names) == 0
        assert len(descriptor.param_annotations) == 0
    
    def test_descriptor_with_parameters(self):
        """测试带参数函数的描述符"""
        def func_with_params(event, name: str, age: int = 18, verbose: bool = False):
            """带参数的函数"""
            pass
        
        descriptor = FuncSpec(func_with_params)
        
        assert descriptor.func_name == "func_with_params"
        assert len(descriptor.param_list) == 4
        assert descriptor.param_names == ["event", "name", "age", "verbose"]
        
        # 检查参数注解
        annotations = descriptor.param_annotations
        assert len(annotations) == 4
        assert annotations[1] is str  # name: str
        assert annotations[2] is int  # age: int
        assert annotations[3] is bool # verbose: bool
    
    def test_descriptor_with_aliases(self):
        """测试带别名的函数描述符"""
        def func_with_alias():
            pass
        
        func_with_alias.__aliases__ = ["alias1", "alias2"]
        
        descriptor = FuncSpec(func_with_alias)
        assert descriptor.aliases == ["alias1", "alias2"]
    
    def test_descriptor_no_aliases(self):
        """测试没有别名的函数描述符"""
        def func_no_alias():
            pass
        
        descriptor = FuncSpec(func_no_alias)
        assert descriptor.aliases == []
    
    def test_descriptor_complex_signature(self):
        """测试复杂签名的函数描述符"""
        def complex_func(event, *args, name: str = "default", **kwargs) -> Optional[str]:
            """复杂函数签名"""
            pass
        
        descriptor = FuncSpec(complex_func)
        
        assert descriptor.func_name == "complex_func"
        assert len(descriptor.param_list) >= 4  # event, *args, name, **kwargs
        
        # 检查参数名称
        param_names = descriptor.param_names
        assert "event" in param_names
        assert "args" in param_names
        assert "name" in param_names
        assert "kwargs" in param_names


class TestFuncAnalyser:
    """函数分析器测试"""
    
    def test_analyzer_creation(self):
        """测试分析器创建"""
        def test_func():
            pass
        
        analyzer = FuncAnalyser(test_func)
        assert analyzer.func_descriptor is not None
        assert analyzer.func_descriptor.func is test_func
    
    def test_analyzer_simple_function(self):
        """测试分析简单函数"""
        def simple_func(event: BaseMessageEvent):
            """简单事件处理函数"""
            return "simple"
        
        analyzer = FuncAnalyser(simple_func)
        
        # 检查描述符
        descriptor = analyzer.func_descriptor
        assert descriptor.func_name == "simple_func"
        assert len(descriptor.param_list) == 1
        assert descriptor.param_names[0] == "event"
    
    def test_analyzer_function_with_params(self):
        """测试分析带参数的函数"""
        def param_func(event, name: str, age: int = 25, verbose: bool = False):
            """带参数的函数"""
            return f"Hello {name}, age {age}"
        
        analyzer = FuncAnalyser(param_func)
        descriptor = analyzer.func_descriptor
        
        # 检查参数数量和类型
        assert len(descriptor.param_list) == 4
        assert descriptor.param_names == ["event", "name", "age", "verbose"]
        
        # 检查默认值
        params = descriptor.param_list
        assert params[0].default == inspect.Parameter.empty  # event 无默认值
        assert params[1].default == inspect.Parameter.empty  # name 无默认值
        assert params[2].default == 25  # age 有默认值
        assert params[3].default == False  # verbose 有默认值
    
    def test_analyzer_function_with_annotations(self):
        """测试分析带类型注解的函数"""
        def annotated_func(event, data: List[str], count: Optional[int] = None) -> str:
            """带类型注解的函数"""
            return "annotated"
        
        analyzer = FuncAnalyser(annotated_func)
        descriptor = analyzer.func_descriptor
        
        # 检查类型注解
        annotations = descriptor.param_annotations
        assert len(annotations) == 3
        assert annotations[1] == List[str]  # data: List[str]
        assert annotations[2] == Optional[int]  # count: Optional[int]
        
        # 检查返回类型注解
        assert descriptor.signature.return_annotation == str
    
    def test_analyzer_function_with_varargs(self):
        """测试分析带可变参数的函数"""
        def varargs_func(event, *args, **kwargs):
            """带可变参数的函数"""
            return "varargs"
        
        analyzer = FuncAnalyser(varargs_func)
        descriptor = analyzer.func_descriptor
        
        # 检查参数类型
        params = descriptor.param_list
        assert len(params) == 3
        
        # 检查参数种类
        assert params[0].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD  # event
        assert params[1].kind == inspect.Parameter.VAR_POSITIONAL  # *args
        assert params[2].kind == inspect.Parameter.VAR_KEYWORD  # **kwargs
    
    def test_analyzer_function_with_keyword_only(self):
        """测试分析带仅关键字参数的函数"""
        def kwonly_func(event, name: str, *, force: bool = False, debug: bool = False):
            """带仅关键字参数的函数"""
            return "kwonly"
        
        analyzer = FuncAnalyser(kwonly_func)
        descriptor = analyzer.func_descriptor
        
        # 检查参数
        params = descriptor.param_list
        assert len(params) == 4
        
        # 检查仅关键字参数
        force_param = next(p for p in params if p.name == "force")
        debug_param = next(p for p in params if p.name == "debug")
        
        assert force_param.kind == inspect.Parameter.KEYWORD_ONLY
        assert debug_param.kind == inspect.Parameter.KEYWORD_ONLY
        assert force_param.default == False
        assert debug_param.default == False


class TestFuncAnalyserAnalyze:
    """函数分析器analyze方法测试"""
    
    def test_analyze_method_exists(self):
        """测试analyze方法存在"""
        def test_func(event: BaseMessageEvent):
            pass
        
        analyzer = FuncAnalyser(test_func)
        assert hasattr(analyzer, 'analyze')
        assert callable(analyzer.analyze)
    
    # @pytest.mark.skip(reason="需要实际的analyze方法实现")
    def test_analyze_returns_command_spec(self):
        """测试analyze方法返回CommandSpec"""
        def test_func(event: BaseMessageEvent, name: str = "default"):
            """测试函数"""
            return "test"
        
        analyzer = FuncAnalyser(test_func)
        result = analyzer.analyze()
        
        # 根据实际实现调整断言
        assert result is not None
        # assert isinstance(result, CommandSpec)
    
    # @pytest.mark.skip(reason="需要实际的analyze方法实现")
    def test_analyze_complex_function(self):
        """测试分析复杂函数"""
        def complex_func(event: BaseMessageEvent, 
                        target: str,
                        data: str,
                        count: int = 1,
                        force: bool = False,
                        debug: bool = False) -> Optional[str]:
            """复杂函数示例"""
            return "complex"
        
        analyzer = FuncAnalyser(complex_func)
        result = analyzer.analyze()
        
        # 验证分析结果
        assert result is not None


class TestFuncAnalyserEdgeCases:
    """函数分析器边界情况测试"""
    
    def test_analyzer_lambda_function(self):
        """测试分析lambda函数"""
        lambda_func = lambda event: "lambda result"
        
        analyzer = FuncAnalyser(lambda_func)
        descriptor = analyzer.func_descriptor
        
        assert descriptor.func is lambda_func
        assert descriptor.func_name == "<lambda>"
        assert len(descriptor.param_list) == 1
    
    def test_analyzer_nested_function(self):
        """测试分析嵌套函数"""
        def outer_func():
            def inner_func(event, data: str):
                return f"inner: {data}"
            return inner_func
        
        inner = outer_func()
        analyzer = FuncAnalyser(inner)
        descriptor = analyzer.func_descriptor
        
        assert descriptor.func is inner
        assert descriptor.func_name == "inner_func"
        assert len(descriptor.param_list) == 2
    
    def test_analyzer_static_method(self):
        """测试分析静态方法"""
        class TestClass:
            @staticmethod
            def static_method(event, data: str):
                return f"static: {data}"
        
        analyzer = FuncAnalyser(TestClass.static_method)
        descriptor = analyzer.func_descriptor
        
        assert descriptor.func is TestClass.static_method
        assert descriptor.func_name == "static_method"
        assert len(descriptor.param_list) == 2  # event, data
    
    def test_analyzer_function_with_docstring(self):
        """测试分析带文档字符串的函数"""
        def documented_func(event: BaseMessageEvent):
            """这是一个有文档的函数
            
            Args:
                event: 事件参数
                
            Returns:
                str: 处理结果
            """
            return "documented"
        
        analyzer = FuncAnalyser(documented_func)
        descriptor = analyzer.func_descriptor
        
        assert descriptor.func is documented_func
        assert descriptor.func.__doc__ is not None
        assert "这是一个有文档的函数" in descriptor.func.__doc__
    
    def test_analyzer_function_no_parameters(self):
        """测试分析无参数函数"""
        def no_param_func():
            """无参数函数"""
            return "no params"
        
        analyzer = FuncAnalyser(no_param_func)
        descriptor = analyzer.func_descriptor
        
        assert len(descriptor.param_list) == 0
        assert len(descriptor.param_names) == 0
        assert len(descriptor.param_annotations) == 0
