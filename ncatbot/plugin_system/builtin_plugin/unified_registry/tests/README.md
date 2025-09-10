# UnifiedRegistry 模块测试

这是 `unified_registry` 模块的全面测试套件，基于 pytest 框架构建。

## 📁 测试结构

```
tests/
├── README.md                      # 本文件
├── conftest.py                     # 全局测试配置和fixtures
├── __init__.py                     # 测试包初始化
├── test_unified_registry_plugin.py # 主插件测试
├── filter_system/                 # 过滤器系统测试
│   ├── __init__.py
│   ├── test_builtin_filters.py     # 内置过滤器测试
│   ├── test_filter_registry.py     # 过滤器注册器测试
│   ├── test_filter_validator.py    # 过滤器验证器测试
│   └── test_filter_integration.py  # 过滤器集成测试
├── command_system/                 # 命令系统测试
│   ├── __init__.py
│   ├── test_func_analyzer.py       # 函数分析器测试
│   ├── test_tokenizer.py          # 词法分析器测试
│   ├── test_message_tokenizer.py  # 消息分词器测试
│   ├── test_registry.py           # 命令注册器测试
│   └── test_command_integration.py # 命令系统集成测试
├── trigger/                        # 触发器系统测试
│   ├── __init__.py
│   ├── test_preprocessor.py        # 预处理器测试
│   ├── test_resolver.py           # 命令解析器测试
│   ├── test_binder.py             # 参数绑定器测试
│   └── test_trigger_integration.py # 触发器集成测试
└── integration/                    # 集成测试
    ├── __init__.py
    ├── test_full_workflow.py       # 完整工作流测试
    └── test_event_handling.py      # 事件处理测试
```

## 🧪 测试覆盖范围

### 单元测试
- ✅ **主插件** (`UnifiedRegistryPlugin`): 插件生命周期、事件处理、函数执行
- ✅ **过滤器系统**: 内置过滤器、注册器、验证器、装饰器
- ✅ **命令系统**: 函数分析器、分词器、注册器、规格管理
- ✅ **触发器系统**: 预处理器、解析器、参数绑定器

### 集成测试
- ✅ **完整工作流**: 从消息接收到命令执行的端到端流程
- ✅ **事件处理**: 各种事件类型的处理和过滤
- ✅ **异步处理**: 并发命令执行和事件处理
- ✅ **错误处理**: 异常情况的优雅处理

### 边界情况测试
- ✅ **输入验证**: 空消息、异常格式、特殊字符
- ✅ **权限验证**: 管理员权限、用户权限检查
- ✅ **状态管理**: 注册器状态、组件隔离

## 🚀 运行测试

### 前置条件

1. **激活虚拟环境**：
   ```bash
   .\.venv\Scripts\activate  # Windows
   # 或
   source .venv/bin/activate  # Linux/Mac
   ```

2. **安装依赖**：
   ```bash
   pip install pytest pytest-asyncio
   ```

### 基本运行

```bash
# 运行所有测试
pytest ncatbot/plugin_system/builtin_plugin/unified_registry/tests/

# 运行特定模块测试
pytest ncatbot/plugin_system/builtin_plugin/unified_registry/tests/filter_system/

# 运行特定测试文件
pytest ncatbot/plugin_system/builtin_plugin/unified_registry/tests/test_unified_registry_plugin.py

# 运行特定测试类
pytest ncatbot/plugin_system/builtin_plugin/unified_registry/tests/test_unified_registry_plugin.py::TestUnifiedRegistryPlugin

# 运行特定测试方法
pytest ncatbot/plugin_system/builtin_plugin/unified_registry/tests/test_unified_registry_plugin.py::TestUnifiedRegistryPlugin::test_plugin_initialization
```

### 详细输出

```bash
# 显示详细输出
pytest -v ncatbot/plugin_system/builtin_plugin/unified_registry/tests/

# 显示测试覆盖率
pytest --cov=ncatbot.plugin_system.builtin_plugin.unified_registry ncatbot/plugin_system/builtin_plugin/unified_registry/tests/

# 生成HTML覆盖率报告
pytest --cov=ncatbot.plugin_system.builtin_plugin.unified_registry --cov-report=html ncatbot/plugin_system/builtin_plugin/unified_registry/tests/
```

### 并行运行

```bash
# 安装 pytest-xdist
pip install pytest-xdist

# 并行运行测试
pytest -n auto ncatbot/plugin_system/builtin_plugin/unified_registry/tests/
```

### 调试模式

```bash
# 在第一个失败时停止
pytest -x ncatbot/plugin_system/builtin_plugin/unified_registry/tests/

# 显示详细错误信息
pytest --tb=long ncatbot/plugin_system/builtin_plugin/unified_registry/tests/

# 进入调试模式
pytest --pdb ncatbot/plugin_system/builtin_plugin/unified_registry/tests/
```

## 🔧 测试配置

### pytest.ini 配置示例

在项目根目录创建 `pytest.ini`：

```ini
[tool:pytest]
testpaths = ncatbot/plugin_system/builtin_plugin/unified_registry/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v 
    --strict-markers
    --tb=short
    --asyncio-mode=auto
markers = 
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### 环境变量

```bash
# 设置日志级别
export NCATBOT_LOG_LEVEL=DEBUG

# 禁用某些警告
export PYTHONWARNINGS=ignore::DeprecationWarning
```

## 📊 测试指标

### 预期覆盖率目标
- **单元测试覆盖率**: >90%
- **集成测试覆盖率**: >80%
- **整体代码覆盖率**: >85%

### 性能指标
- **测试执行时间**: <2分钟（全套测试）
- **单个测试文件**: <10秒
- **内存使用**: <100MB

## 🐛 常见问题

### 1. 虚拟环境问题
```bash
# 确保虚拟环境已激活
where python  # Windows
which python  # Linux/Mac

# 重新安装依赖
pip install -r requirements.txt
```

### 2. 导入错误
```bash
# 确保项目根目录在 Python 路径中
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 3. 异步测试问题
```bash
# 确保安装了 pytest-asyncio
pip install pytest-asyncio

# 检查测试标记
pytest --markers
```

### 4. Mock 对象问题
```bash
# 清理缓存
pytest --cache-clear

# 重新运行失败的测试
pytest --lf
```

## 📝 编写新测试

### 1. 单元测试模板

```python
import pytest
from unittest.mock import Mock, patch

class TestNewComponent:
    def test_basic_functionality(self):
        # 1. 准备
        component = NewComponent()
        
        # 2. 执行
        result = component.do_something()
        
        # 3. 验证
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        component = NewComponent()
        result = await component.do_async_something()
        assert result is not None
```

### 2. 集成测试模板

```python
@pytest.mark.asyncio
async def test_component_integration(unified_plugin, clean_registries):
    # 1. 设置
    execution_log = []
    
    # 2. 注册组件
    @command_registry.command("test")
    def test_command(event):
        execution_log.append("executed")
        return "result"
    
    # 3. 执行完整流程
    mock_event = MockMessageEvent("/test")
    await unified_plugin.handle_message_event(mock_event)
    
    # 4. 验证
    assert "executed" in execution_log
```

### 3. Fixture 使用

```python
def test_with_mock_user(mock_user):
    assert mock_user.user_id == "123456"

def test_with_clean_registries(clean_registries):
    # 在这里注册的命令/过滤器会在测试后自动清理
    pass

async def test_with_unified_plugin(unified_plugin):
    # 使用预配置的插件实例
    assert unified_plugin.name == "UnifiedRegistryPlugin"
```

## 🚨 注意事项

1. **测试隔离**: 每个测试应该独立运行，不依赖其他测试的状态
2. **清理资源**: 使用 `clean_registries` fixture 确保测试后清理
3. **异步测试**: 使用 `pytest.mark.asyncio` 标记异步测试
4. **Mock使用**: 适当使用 Mock 对象隔离外部依赖
5. **断言明确**: 使用清晰、具体的断言消息

## 📈 持续集成

### GitHub Actions 示例

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    - name: Run tests
      run: |
        pytest ncatbot/plugin_system/builtin_plugin/unified_registry/tests/ \
               --cov=ncatbot.plugin_system.builtin_plugin.unified_registry \
               --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## 📞 获取帮助

如果在运行测试时遇到问题：

1. 检查本文档的常见问题部分
2. 确保所有依赖已正确安装
3. 检查虚拟环境是否已激活
4. 查看测试输出的详细错误信息

测试愉快！🎉
