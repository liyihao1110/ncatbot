# UnifiedRegistry 文档验证示例

本目录包含对 `docs/plugin_system/unified_registry` 中文档片段的可运行验证示例。示例使用 `ncatbot.utils.testing` 的 TestClient/TestHelper 在 Mock 环境下运行，无需真实 QQ 客户端。

## 目录结构

- `quick_start/`
  - `plugins/`：快速开始文档涉及到的演示插件
  - `test_basic.py`：基础、参数、选项、别名
  - `test_permissions_and_filters.py`：group_only/private_only/admin_only 与纯过滤器
  - `test_full_example.py`：完整插件示例（集成态）
  - `test_external_funcs.py`：类外/类内命令与管理员命令
- `test_readme.py`：对应 `UnifiedRegistry-README.md` “快速开始”片段的验证
- `filters/`：对应 `UnifiedRegistry-过滤器系统.md` 的验证
  - `plugins/`：过滤器相关演示插件
  - `test_builtin_filters.py`：内置过滤器与 on_message
  - `test_combo_filters.py`：组合装饰器与一次性注册多个过滤器
  - `test_custom_filters.py`：自定义过滤器与按名称绑定
  - `test_level_and_cooldown.py`：过滤器类与冷却时间示例
- `params/`：对应 `UnifiedRegistry-参数解析.md` 的验证
  - `plugins/`：参数解析相关演示插件
  - `test_basic_syntax.py`：基础参数与引用字符串
  - `test_options_and_named.py`：选项、命名参数、选项组与组合语法
  - `test_types_and_errors.py`：类型转换、布尔值与错误处理
  - `test_media_and_advanced.py`：非文本元素（图片/@用户）与补充场景
- `commands/`：对应 `UnifiedRegistry-命令系统.md` 的验证
  - `plugins/`：命令系统相关演示插件
  - `test_basic_and_alias.py`：基础命令与别名
  - `test_external_command.py`：类外命令
  - `test_groups.py`：命令分组与嵌套
  - `test_complex.py`：复杂功能（backup/send）
 - `cases/`：对应 `UnifiedRegistry-实战案例.md` 的验证
   - `plugins/`：实战案例相关演示插件
   - `test_qa_bot.py`：简单问答机器人
   - `test_group_management.py`：群管理功能
   - `test_info_query.py`：信息查询服务
   - `test_data_processing.py`：数据处理与分析
   - `test_web_api.py`：Web API 集成（模拟）

## 运行前准备（PowerShell）

```powershell
.\.venv\Scripts\activate
```

确保当前目录为项目根目录（包含 `pyproject.toml`）。

## 运行命令（python -m）

- 运行“快速开始-基础/参数/选项/别名”
```powershell
python -m examples.unified_registry.quick_start.test_basic
```

- 运行“快速开始-权限与过滤器”
```powershell
python -m examples.unified_registry.quick_start.test_permissions_and_filters
```

- 运行“快速开始-完整示例（集成态）”
```powershell
python -m examples.unified_registry.quick_start.test_full_example
```

- 运行“快速开始-类外函数注册与管理员命令”
```powershell
python -m examples.unified_registry.quick_start.test_external_funcs
```

- 运行 README 示例验证
```powershell
python -m examples.unified_registry.test_readme
```

- 运行 过滤器系统-内置过滤器 与 on_message
```powershell
python -m examples.unified_registry.filters.test_builtin_filters
```

- 运行 过滤器系统-组合装饰器 与 多过滤器
```powershell
python -m examples.unified_registry.filters.test_combo_filters
```

- 运行 过滤器系统-自定义过滤器
```powershell
python -m examples.unified_registry.filters.test_custom_filters
```

- 运行 过滤器系统-过滤器类 与 冷却时间
```powershell
python -m examples.unified_registry.filters.test_level_and_cooldown
```

- 运行 参数解析-基础语法与引用
```powershell
python -m examples.unified_registry.params.test_basic_syntax
```

- 运行 参数解析-选项与命名参数
```powershell
python -m examples.unified_registry.params.test_options_and_named
```

- 运行 参数解析-类型与错误处理
```powershell
python -m examples.unified_registry.params.test_types_and_errors
```

- 运行 参数解析-非文本元素与高级
```powershell
python -m examples.unified_registry.params.test_media_and_advanced
```

- 运行 命令系统-基础与别名
```powershell
python -m examples.unified_registry.commands.test_basic_and_alias
```

- 运行 命令系统-类外命令
```powershell
python -m examples.unified_registry.commands.test_external_command
```

- 运行 命令系统-分组与嵌套
```powershell
python -m examples.unified_registry.commands.test_groups
```

- 运行 命令系统-复杂功能
```powershell
python -m examples.unified_registry.commands.test_complex
```

- 运行 实战案例-问答机器人
```powershell
python -m examples.unified_registry.cases.test_qa_bot
```

- 运行 实战案例-群管理
```powershell
python -m examples.unified_registry.cases.test_group_management
```

- 运行 实战案例-信息查询
```powershell
python -m examples.unified_registry.cases.test_info_query
```

- 运行 实战案例-数据处理
```powershell
python -m examples.unified_registry.cases.test_data_processing
```

- 运行 实战案例-Web API（模拟）
```powershell
python -m examples.unified_registry.cases.test_web_api
```

## 说明

- 管理员权限用例通过临时替换 `ncatbot.utils.status.global_access_manager.user_has_role` 进行模拟，测试前后会恢复。
- 运行成功后，控制台会输出断言通过的提示文本；若断言失败，请根据输出调整文档或示例。
