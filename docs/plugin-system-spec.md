# 插件系统（Plugin System）详细规范

## 目标与功能
- 提供插件的加载、卸载和管理功能
- 实现事件发布订阅系统 (EventBus)，支持消息和事件处理
- 提供基于角色的访问控制系统 (RBAC)，支持用户和群组权限
- 实现定时任务调度系统
- 支持插件功能的抽象和管理
- 支持多账号场景下的事件隔离
- 提供内置管理功能，允许通过 QQ 消息管理插件

## 核心组件
1. **Plugin Loader**
   - `PluginLoader` 负责发现、加载和管理插件
   - 支持热重载插件
   - 处理插件依赖关系
   - 管理插件生命周期（初始化和卸载）
   - 支持插件黑白名单过滤
   - 兼容旧版本插件注册方式 (`CompatibleEnrollment`)
   - 提供获取插件元数据的函数 (`get_plugin_metadata`)

2. **元数据管理**
   - 提供统一的插件元数据结构，包含：
     - 基本信息（名称、版本、作者、描述）
     - 功能列表及其权限要求
     - 配置项列表
     - 依赖关系
     - 安装时间和更新记录
   - 支持元数据的序列化和反序列化
   - 提供元数据检索和查询功能

3. **Event System**
   - `EventBus` 实现事件发布和订阅
   - 支持事件优先级
   - 支持正则表达式匹配事件类型
   - 实现事件异步处理
   - 提供事件源和数据标准化
   - 通过 `Event` 类封装事件数据和源信息
   - 提供 `EventSource` 表示事件来源（用户ID、群ID）

4. **Access Controller**
   - `RBACManager` 实现基于角色的访问控制
   - 支持用户权限和群组权限
   - 实现权限路径和继承体系
   - 支持白名单和黑名单模式
   - 提供权限检查和验证接口
   - 全局访问控制器单例 `get_global_access_controller()`
   - 为插件提供权限管理接口，允许插件定义自己的权限路径

5. **Function System**
   - `Func` 类抽象插件功能，专注于消息处理
   - 提供多种功能激活方式：
     - 前缀匹配（prefix）
     - 正则匹配（regex）
     - 自定义过滤器（filter）
   - 集成权限系统进行鉴权
   - 支持自定义功能元数据（描述、用法、示例、标签）
   - 内置功能用于管理所有插件

6. **Configuration System**
   - `Conf` 类管理插件配置
   - 支持配置项的权限控制
   - 提供配置的查询和修改接口
   - 支持配置值类型转换
   - 支持配置更改回调函数

7. **Base Plugin**
   - `BasePlugin` 为插件提供标准化接口
   - 封装插件元数据和基本功能
   - 管理插件生命周期（加载和卸载）
   - 提供生命周期钩子（`on_load`, `on_close`, `_init_`, `_close_`）
   - 集成事件处理、定时任务和内置功能支持
   - 提供数据持久化和工作空间管理

## 接口规范
- **Plugin 开发接口**
   ```python
   class MyPlugin(BasePlugin):
       name = "my_plugin"  # 插件名称（必需）
       version = "1.0.0"   # 插件版本（必需）
       author = "Author"   # 插件作者（可选）
       info = "My plugin description" # 插件描述（可选）
       dependencies = {}   # 依赖项（可选）
       save_type = "json"  # 数据保存类型（可选）

       def _init_(self):
           # 同步初始化，注册功能和配置
           self.register_function(
               func=self.hello,           # 功能实现函数
               name="hello",              # 功能名称
               prefix="hello",            # 前缀匹配
               permission="user",         # 所需权限
               description="发送问候",     # 功能描述
               usage="发送 hello 获取回复", # 功能用法
           )
           
           self.register_config(
               key="greeting",            # 配置键
               default="Hello, world!",   # 默认值
               description="问候语"        # 配置描述
           )
           
           # 注册事件处理器
           self.register_handler("group_message", self.handle_group_message)
           
           # 添加定时任务
           self.add_scheduled_task("0 * * * *", self.scheduled_task)
           
           # 定义插件权限路径
           self.define_permission_path("feature1", "使用特性1的权限")
           self.define_permission_path("feature2", "使用特性2的权限")

       async def on_load(self):
           # 异步初始化
           pass

       async def hello(self, message):
           greeting = self.get_config("greeting")
           message.reply_text_sync(greeting)
           
       async def handle_group_message(self, event):
           # 处理群消息事件
           pass
           
       async def scheduled_task(self):
           # 定时任务
           pass
           
       def _close_(self):
           # 同步清理
           pass
           
       async def on_close(self):
           # 异步清理
           pass
   ```

- **元数据获取接口**
   ```python
   # 获取插件元数据
   metadata = plugin_loader.get_plugin_metadata("plugin_name")
   
   # 获取所有插件的元数据
   all_metadata = plugin_loader.get_all_plugins_metadata()
   
   # 元数据结构示例
   {
       "name": "plugin_name",
       "version": "1.0.0",
       "author": "Author",
       "info": "Plugin description",
       "dependencies": {"python_package": ">=1.0.0"},
       "functions": [
           {
               "name": "hello",
               "description": "发送问候",
               "usage": "发送 hello 获取回复",
               "permission": "user"
           }
       ],
       "configs": [
           {
               "key": "greeting",
               "description": "问候语",
               "default": "Hello, world!",
               "value_type": "str"
           }
       ],
       "installed_time": "2023-01-01 12:00:00",
       "last_updated": "2023-01-02 14:30:00",
       "enabled": true
   }
   ```

- **插件权限管理接口**
   ```python
   # 在插件中定义权限路径
   def define_permission_path(self, path, description=""):
       """
       定义插件特定的权限路径
       
       Args:
           path: 相对于插件名称的路径，如 "feature1"
           description: 权限描述
       
       Returns:
           完整的权限路径 (如 "my_plugin.feature1")
       """
       full_path = f"{self.name}.{path}"
       # 获取全局访问控制器
       access_controller = get_global_access_controller()
       # 创建权限路径
       access_controller.create_permission_path(full_path, description)
       return full_path
       
   # 检查用户是否有特定权限
   def check_permission(self, user_id, path, group_id=None):
       """
       检查用户是否有特定权限
       
       Args:
           user_id: 用户ID
           path: 相对于插件名称的路径，如 "feature1"
           group_id: 群组ID (可选)
           
       Returns:
           bool: 是否有权限
       """
       full_path = f"{self.name}.{path}"
       # 获取全局访问控制器
       access_controller = get_global_access_controller()
       # 创建事件源
       source = EventSource(user_id, group_id or "root")
       # 检查权限
       return access_controller.with_permission(
           path=full_path,
           source=source
       )
   ```

- **Event Bus 接口**
   ```python
   # 订阅事件
   handler_id = event_bus.subscribe(
       event_type="group_message",
       handler=handle_group_message,
       priority=10
   )

   # 发布事件
   await event_bus.publish_async(Event(
       type="group_message",
       data=message,
       source=EventSource(user_id, group_id)
   ))

   # 取消订阅
   event_bus.unsubscribe(handler_id)
   ```

- **功能注册接口**
   ```python
   # 在插件中注册功能
   self.register_function(
       func=self.command_handler,    # 处理函数
       name="command",               # 功能名称
       prefix="/cmd",                # 前缀匹配（可选）
       regex=r"^/\w+",              # 正则匹配（可选）
       filter=custom_filter,         # 自定义过滤器（可选）
       permission="user",            # 权限组
       permission_raise=False,       # 是否提权
       reply=True,                   # 权限不足时是否回复
       description="命令功能",        # 描述
       usage="使用方法: /cmd 参数",    # 用法
       examples=["示例1", "示例2"],   # 示例
       tags=["命令", "工具"]          # 标签
   )
   ```

- **配置注册接口**
   ```python
   # 在插件中注册配置
   self.register_config(
       key="config_key",              # 配置键
       default="默认值",               # 默认值
       on_change=self.on_config_change, # 配置变更回调
       description="配置描述",         # 描述
       value_type="str",              # 值类型
       allowed_values=["值1", "值2"]   # 允许的值
   )
   
   # 配置变更回调
   async def on_config_change(self, new_value, message):
       # 处理配置变更
       pass
   ```

- **权限系统接口**
   ```python
   # 获取全局访问控制器
   access_controller = get_global_access_controller()
   
   # 创建权限路径
   access_controller.create_permission_path("plugin.feature", "权限描述")

   # 分配权限
   access_controller.assign_permissions_to_role(
       role_name="admin",
       path="plugin.feature",
       mode="white"
   )

   # 检查权限
   has_permission = access_controller.with_permission(
       path="plugin.feature",
       source=EventSource(user_id, group_id)
   )
   
   # 将角色分配给用户
   access_controller.assign_role_to_user(user_id, "admin")
   
   # 将角色分配给群组
   access_controller.assign_role_to_group(group_id, "admin")
   ```

## 内置功能
1. **插件管理功能** (`plg`)
   - 列出已加载插件
   - 启用/禁用插件
   - 重载插件
   - 查看插件详细信息和元数据

2. **配置管理功能** (`cfg`)
   - 查看和修改配置
   - 支持基于权限的配置访问
   - 通过权限路径 `ncatbot.cfg.<plugin_name>.<key>` 控制访问

3. **帮助功能** (`help`)
   - 显示功能列表和用法
   - 提供特定功能的详细帮助

4. **权限管理功能** (`acs`)
   - 管理用户和群组的权限
   - 授予和撤销特定功能的访问权限
   
5. **管理员设置功能** (`sm`)
   - 设置和取消用户的管理员身份

6. **重载功能** (`reload`)
   - 重新加载所有插件
   - 热更新系统配置 