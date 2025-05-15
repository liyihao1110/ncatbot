# CLI 模块详细规范

## 目标与功能
- 提供命令行界面，便于用户和开发者管理 NcatBot
- 管理插件的安装、卸载和更新
- 提供插件系统权限的后台管理功能
- 支持开发者创建和发布插件
- 管理 NcatBot 本体的更新和配置
- 提供 NcatBot 的启动控制

## 核心组件
1. **Command Registry**
   - `registry.py` 管理命令注册和执行
   - 提供命令帮助和描述
   - 支持命令别名
   - 处理命令参数和选项
   - 支持命令分类
   - 支持 QQ 号要求检查

2. **Plugin Management**
   - `plugin_commands.py` 实现插件管理命令
   - 安装、卸载、更新和列出插件
   - 创建新插件模板
   - 检查插件依赖
   - 管理插件元数据

3. **System Management**
   - `system_commands.py` 管理系统级命令
   - 启动和停止 NcatBot
   - 检查系统状态
   - 更新 NcatBot 本体
   - 管理 QQ 号配置

4. **Information Commands**
   - `info_commands.py` 提供信息查询命令
   - 显示系统信息
   - 查看日志
   - 检查配置状态
   - 显示命令帮助

5. **Utilities**
   - `utils.py` 提供 CLI 工具函数
   - 获取当前配置的 QQ 号
   - 处理用户输入
   - 格式化命令输出
   - 插件信息管理

6. **Main Entry**
   - `main.py` 提供 CLI 入口点
   - 解析命令行参数
   - 支持交互模式和命令行模式
   - 设置工作目录
   - 处理退出和错误

## 命令分类
1. **Information 命令**
   - `help [命令名|分类名]` - 显示帮助信息
   - `version` - 显示版本信息
   - `info` - 显示系统信息
   - `categories` - 显示命令分类

2. **System 命令**
   - `setqq` - 设置 QQ 号
   - `start [-d|-D|--debug]` - 启动 NcatBot
   - `update` - 更新 NcatBot
   - `exit` - 退出 CLI

3. **Plugin 命令**
   - `install <插件名> [--fix]` - 安装插件
   - `remove <插件名>` - 卸载插件
   - `list` - 列出已安装插件
   - `list_remote` - 列出远程插件
   - `create <插件名>` - 创建插件模板

## 命令注册接口
```python
@registry.register(
    name="command_name",
    description="命令描述",
    usage="命令用法",
    help_text="详细帮助信息",
    aliases=["别名1", "别名2"],
    category="命令分类",
    requires_qq=True/False
)
def command_function(*args):
    # 命令实现
    pass
```

## 命令执行流程
1. 解析命令行参数
2. 设置工作目录
3. 检查命令模式（交互/命令行）
4. 执行命令
   - 检查命令是否存在
   - 检查命令别名
   - 检查 QQ 号要求
   - 执行命令函数
5. 处理错误和异常

## 错误处理
- 命令不存在
- 参数错误
- QQ 号未设置
- 插件操作失败
- 系统错误

## 日志系统
- 使用 NcatBot 的日志系统
- 记录命令执行
- 记录错误信息
- 支持调试模式

## 测试规范
1. **单元测试**
   - 命令注册测试
   - 命令执行测试
   - 参数解析测试
   - 错误处理测试

2. **集成测试**
   - 命令流程测试
   - 插件管理测试
   - 系统命令测试
   - 交互模式测试

3. **功能测试**
   - 帮助系统测试
   - 插件操作测试
   - 系统操作测试
   - 错误处理测试

## 使用示例
1. **命令行模式**
```bash
# 显示帮助
ncatbot -c help

# 启动 NcatBot
ncatbot -c start

# 安装插件
ncatbot -c install TestPlugin

# 显示版本
ncatbot --version
```

2. **交互模式**
```bash
# 启动交互模式
ncatbot

# 显示帮助
> help

# 查看分类
> categories

# 启动 NcatBot
> start
```

## 开发指南
1. **添加新命令**
   - 在适当的模块中定义命令函数
   - 使用 `@registry.register` 装饰器注册命令
   - 添加命令文档和帮助信息
   - 编写单元测试

2. **修改现有命令**
   - 保持向后兼容
   - 更新命令文档
   - 更新单元测试
   - 检查错误处理

3. **错误处理**
   - 使用适当的异常类型
   - 提供清晰的错误信息
   - 记录错误日志
   - 优雅退出

4. **测试编写**
   - 覆盖所有命令
   - 测试错误情况
   - 测试边界条件
   - 保持测试独立性
