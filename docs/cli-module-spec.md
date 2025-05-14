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

2. **Plugin Management**
   - `plugin_commands.py` 实现插件管理命令
   - 安装、卸载、更新和列出插件
   - 创建新插件模板
   - 检查插件依赖

3. **System Management**
   - `system_commands.py` 管理系统级命令
   - 启动和停止 NcatBot
   - 检查系统状态
   - 更新 NcatBot 本体

4. **Information Commands**
   - `info_commands.py` 提供信息查询命令
   - 显示系统信息
   - 查看日志
   - 检查配置状态

5. **Utilities**
   - `utils.py` 提供 CLI 工具函数
   - 获取当前配置的 QQ 号
   - 处理用户输入
   - 格式化命令输出

6. **Main Entry**
   - `main.py` 提供 CLI 入口点
   - 解析命令行参数
   - 支持交互模式和命令行模式
   - 设置工作目录
   - 处理退出和错误

## 接口规范
- **命令注册接口**
   ```python
   # 注册命令
   @registry.register_command(
       name="run",
       aliases=["r", "start"],
       description="启动 NcatBot",
       usage="run [选项]"
   )
   def run_command(*args):
       # 命令实现
   ```

- **插件管理接口**
   ```python
   # 安装插件
   def install_plugin(plugin_name, version=None, source=None):
       # 实现插件安装

   # 卸载插件
   def uninstall_plugin(plugin_name):
       # 实现插件卸载

   # 更新插件
   def update_plugin(plugin_name, version=None):
       # 实现插件更新
   ```

- **发布工具接口**
   ```python
   # 发布插件
   def publish_plugin(plugin_path, registry_url=None):
       # 实现插件发布
   ```

## 命令列表
1. **基本命令**
   - `help` - 显示帮助信息
   - `exit` / `q` - 退出 CLI
   - `run` / `r` / `start` / `s` - 启动 NcatBot

2. **插件命令**
   - `install` / `i` - 安装插件
   - `uninstall` / `u` - 卸载插件
   - `update` - 更新插件
   - `list` / `ls` - 列出已安装插件
   - `publish` / `p` - 发布插件
   - `create` / `c` - 创建新插件

3. **系统命令**
   - `config` / `cfg` - 查看和修改配置
   - `info` - 显示系统信息
   - `log` - 查看日志
   - `version` / `v` - 显示版本信息

## 实现方式
- 支持两种运行模式：
  1. **交互模式** - 用户输入命令，CLI 执行命令并显示结果
  2. **命令行模式** - 通过命令行参数直接执行命令

- 提供友好的错误处理和帮助信息
- 支持命令自动补全和历史记录（如可能）
- 保持与旧版 CLI 兼容，并迁移现有 publish 功能 