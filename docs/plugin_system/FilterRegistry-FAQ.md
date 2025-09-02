# FilterRegistry 常见问题解答

## 🤔 常见问题

### 基础使用问题

#### Q1: 为什么我的命令没有响应？

**A:** 检查以下几点：

1. **插件是否正确加载**
   ```python
   # 在插件的 on_load 方法中添加日志
   async def on_load(self):
       self.log.info(f"{self.name} 插件已加载")
   ```

2. **命令是否正确注册**
   ```python
   # 确保使用了 @filter.command() 装饰器
   @filter.command("test")
   async def test_command(self, event: BaseMessageEvent):
       await event.reply("测试命令")
   ```

3. **函数签名是否正确**
   ```python
   # ✅ 正确的函数签名
   async def my_command(self, event: BaseMessageEvent):
       pass
   
   # ❌ 错误的函数签名（缺少 self 参数）
   async def my_command(event: BaseMessageEvent):
       pass
   ```

4. **过滤器是否阻止了执行**
   ```python
   # 检查权限过滤器设置
   @filter.admin_only()  # 确保用户有管理员权限
   async def admin_command(self, event: BaseMessageEvent):
       pass
   ```

#### Q2: 参数解析不工作怎么办？

**A:** 常见参数解析问题：

1. **参数类型不匹配**
   ```python
   @filter.command("calc")
   async def calculate(self, event: BaseMessageEvent, a: int, b: int):
       # 用户输入: "calc abc 123" 
       # 解决: abc 无法转换为 int，函数不会执行
       pass
   ```

2. **参数数量不匹配**
   ```python
   @filter.command("add")
   async def add_numbers(self, event: BaseMessageEvent, a: int, b: int):
       # 用户输入: "add 5" (缺少第二个参数)
       # 解决: 提供默认值或使用可选参数
       pass
   ```

3. **解决方案**
   ```python
   @filter.command("calc")
   async def calculate(self, event: BaseMessageEvent, a: str, b: str):
       try:
           num_a = int(a)
           num_b = int(b)
           result = num_a + num_b
           await event.reply(f"结果: {result}")
       except ValueError:
           await event.reply("❌ 请输入有效的数字")
   ```

#### Q3: 布尔值参数怎么传递？

**A:** 布尔类型参数有特殊的转换规则：

**转换为 `False` 的值：**
- `"false"` (不区分大小写)
- `"0"`

**转换为 `True` 的值：**
- 其他任何值（`"true"`, `"1"`, `"yes"`, `"on"` 等）

```python
@filter.command("设置")
async def set_option(self, event: BaseMessageEvent, enable: bool):
    if enable:
        await event.reply("选项已启用")
    else:
        await event.reply("选项已禁用")
```

**使用示例：**
- `设置 true` ✅ → "选项已启用"
- `设置 1` ✅ → "选项已启用"
- `设置 yes` ✅ → "选项已启用"
- `设置 false` ❌ → "选项已禁用"
- `设置 0` ❌ → "选项已禁用"

#### Q4: 自定义过滤器不生效？

**A:** 检查过滤器函数：

1. **函数签名错误**
   ```python
   # ❌ 错误：参数数量不对
   def my_filter(event):
       return True
   
   # ✅ 正确：简单过滤器
   def my_filter(event: BaseMessageEvent) -> bool:
       return True
   
   # ✅ 正确：高级过滤器
   def my_filter(manager, event: BaseMessageEvent) -> bool:
       return True
   ```

2. **没有返回布尔值**
   ```python
   # ❌ 错误：没有返回值
   def my_filter(event: BaseMessageEvent):
       'special' in event.raw_message
   
   # ✅ 正确：返回布尔值
   def my_filter(event: BaseMessageEvent) -> bool:
       return 'special' in event.raw_message
   ```

3. **过滤器异常**
   ```python
   # ✅ 安全的过滤器
   def safe_filter(event: BaseMessageEvent) -> bool:
       try:
           return some_complex_check(event)
       except Exception as e:
           LOG.error(f"过滤器异常: {e}")
           return False  # 异常时返回 False
   ```

### 权限系统问题

#### Q5: 权限系统如何配置？

**A:** 权限配置步骤：

1. **配置 RBAC 文件**
   ```json
   // data/rbac.json
   {
     "roles": {
       "admin": {
         "permissions": ["*"]
       },
       "user": {
         "permissions": ["basic"]
       }
     },
     "users": {
       "123456789": ["admin"],
       "987654321": ["user"]
     }
   }
   ```

2. **在代码中检查权限**
   ```python
   @filter.admin_only()
   async def admin_command(self, event: BaseMessageEvent):
       await event.reply("管理员功能")
   
   # 或者手动检查
   async def check_permission(self, event: BaseMessageEvent):
       rbac = self.plugin_loader.rbac_manager
       if rbac.user_has_role(event.user_id, "admin"):
           await event.reply("你是管理员")
       else:
           await event.reply("权限不足")
   ```

#### Q5: 如何动态分配权限？

**A:** 动态权限管理：

```python
@filter.root_only()
@filter.command("设置管理员")
async def set_admin(self, event: BaseMessageEvent, user_id: str):
    rbac = self.plugin_loader.rbac_manager
    
    # 分配管理员角色
    rbac.assign_role_to_user(user_id, "admin")
    await event.reply(f"✅ 用户 {user_id} 已设置为管理员")

@filter.root_only()
@filter.command("取消管理员")
async def remove_admin(self, event: BaseMessageEvent, user_id: str):
    rbac = self.plugin_loader.rbac_manager
    
    # 移除管理员角色
    rbac.revoke_role_from_user(user_id, "admin")
    await event.reply(f"✅ 用户 {user_id} 管理员权限已移除")
```

### 性能优化问题

#### Q6: 如何优化插件性能？

**A:** 性能优化建议：

1. **使用缓存**
   ```python
   from functools import lru_cache
   
   class MyPlugin(BasePlugin):
       def __init__(self):
           super().__init__()
           self._cache = {}
       
       @lru_cache(maxsize=1000)
       def get_user_info(self, user_id: str):
           # 缓存用户信息查询
           return database.get_user(user_id)
       
       async def expensive_operation(self, key: str):
           # 使用内存缓存
           if key in self._cache:
               return self._cache[key]
           
           result = await some_expensive_call(key)
           self._cache[key] = result
           return result
   ```

2. **异步处理**
   ```python
   import asyncio
   
   @filter.command("批量查询")
   async def batch_query(self, event: BaseMessageEvent, *user_ids):
       # 并发查询而不是串行
       tasks = [self.get_user_data(uid) for uid in user_ids]
       results = await asyncio.gather(*tasks, return_exceptions=True)
       
       # 处理结果
       for i, result in enumerate(results):
           if isinstance(result, Exception):
               self.log.error(f"查询 {user_ids[i]} 失败: {result}")
   ```

3. **避免阻塞操作**
   ```python
   # ❌ 错误：同步文件操作
   def save_data(self, data):
       with open("data.json", "w") as f:
           json.dump(data, f)
   
   # ✅ 正确：异步文件操作
   async def save_data(self, data):
       import aiofiles
       async with aiofiles.open("data.json", "w") as f:
           await f.write(json.dumps(data))
   ```

#### Q7: 内存使用过高怎么办？

**A:** 内存优化方法：

1. **及时清理缓存**
   ```python
   class MyPlugin(BasePlugin):
       def __init__(self):
           super().__init__()
           self._cache = {}
           self._max_cache_size = 1000
       
       def _cleanup_cache(self):
           if len(self._cache) > self._max_cache_size:
               # 清理最旧的一半缓存
               items = list(self._cache.items())
               items_to_remove = items[:len(items)//2]
               for key, _ in items_to_remove:
                   del self._cache[key]
   ```

2. **使用弱引用**
   ```python
   import weakref
   
   class MyPlugin(BasePlugin):
       def __init__(self):
           super().__init__()
           self._observers = weakref.WeakSet()
   ```

### 数据持久化问题

#### Q8: 如何正确保存插件数据？

**A:** 数据持久化最佳实践：

1. **JSON 文件存储**
   ```python
   import json
   import os
   from pathlib import Path
   
   class MyPlugin(BasePlugin):
       def __init__(self):
           super().__init__()
           self.data_dir = Path("data") / self.name
           self.data_dir.mkdir(parents=True, exist_ok=True)
           self.data_file = self.data_dir / "plugin_data.json"
           self.data = self._load_data()
       
       def _load_data(self):
           if self.data_file.exists():
               try:
                   with open(self.data_file, 'r', encoding='utf-8') as f:
                       return json.load(f)
               except Exception as e:
                   self.log.error(f"加载数据失败: {e}")
           return {}
       
       def _save_data(self):
           try:
               with open(self.data_file, 'w', encoding='utf-8') as f:
                   json.dump(self.data, f, ensure_ascii=False, indent=2)
           except Exception as e:
               self.log.error(f"保存数据失败: {e}")
   ```

2. **数据库存储**
   ```python
   import sqlite3
   import aiosqlite
   
   class MyPlugin(BasePlugin):
       async def init_database(self):
           async with aiosqlite.connect(self.db_path) as db:
               await db.execute("""
                   CREATE TABLE IF NOT EXISTS user_data (
                       user_id TEXT PRIMARY KEY,
                       points INTEGER DEFAULT 0,
                       level INTEGER DEFAULT 1,
                       last_active TEXT
                   )
               """)
               await db.commit()
       
       async def get_user_data(self, user_id: str):
           async with aiosqlite.connect(self.db_path) as db:
               cursor = await db.execute(
                   "SELECT * FROM user_data WHERE user_id = ?", 
                   (user_id,)
               )
               return await cursor.fetchone()
   ```

#### Q9: 数据迁移怎么处理？

**A:** 版本升级和数据迁移：

```python
class MyPlugin(BasePlugin):
    DATA_VERSION = 2  # 当前数据版本
    
    def _load_data(self):
        data = {}
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                self.log.error(f"加载数据失败: {e}")
        
        # 检查数据版本并迁移
        data_version = data.get("_version", 1)
        if data_version < self.DATA_VERSION:
            data = self._migrate_data(data, data_version)
            data["_version"] = self.DATA_VERSION
            self._save_data()
        
        return data
    
    def _migrate_data(self, data, from_version):
        """数据迁移逻辑"""
        if from_version == 1 and self.DATA_VERSION >= 2:
            # 从版本1迁移到版本2
            self.log.info("迁移数据从版本1到版本2")
            
            # 例如：重命名字段
            if "users" in data:
                for user_id, user_data in data["users"].items():
                    if "score" in user_data:
                        user_data["points"] = user_data.pop("score")
        
        return data
```

### 测试相关问题

#### Q10: 如何写好测试？

**A:** 测试最佳实践：

1. **使用测试框架**
   ```python
   from ncatbot.utils.testing import TestClient, TestHelper
   
   async def test_my_plugin():
       client = TestClient()
       helper = TestHelper(client)
       client.start(mock_mode=True)
       
       # 测试命令
       await helper.send_private_message("test", user_id="test_user")
       helper.assert_reply_sent("测试回复")
       
       # 清理
       helper.clear_history()
   ```

2. **模拟外部依赖**
   ```python
   from unittest.mock import AsyncMock, patch
   
   @patch('your_plugin.external_api_call')
   async def test_api_integration(mock_api):
       # 模拟API调用
       mock_api.return_value = {"status": "success", "data": "test"}
       
       # 运行测试
       result = await your_function()
       assert result == "expected_result"
   ```

#### Q11: 测试覆盖率不够怎么办？

**A:** 提高测试覆盖率：

1. **测试所有路径**
   ```python
   async def test_all_paths(self):
       # 测试正常路径
       await helper.send_private_message("calc 5 3", user_id="test_user")
       helper.assert_reply_sent("8")
       
       # 测试错误路径
       await helper.send_private_message("calc abc def", user_id="test_user")
       helper.assert_no_reply()  # 参数错误不应回复
       
       # 测试边界条件
       await helper.send_private_message("calc 0 0", user_id="test_user")
       helper.assert_reply_sent("0")
   ```

2. **使用覆盖率工具**
   ```bash
   pip install coverage
   coverage run -m pytest tests/
   coverage report -m
   coverage html  # 生成HTML报告
   ```

### 部署和维护问题

#### Q12: 如何监控插件运行状态？

**A:** 监控和日志记录：

1. **完善的日志记录**
   ```python
   from ncatbot.utils import get_log
   
   class MyPlugin(BasePlugin):
       def __init__(self):
           super().__init__()
           self.log = get_log(self.name)
       
       @filter.command("process")
       async def process_data(self, event: BaseMessageEvent, data: str):
           self.log.info(f"开始处理数据: {data}")
           
           try:
               result = await self.complex_operation(data)
               self.log.info(f"处理完成: {result}")
               await event.reply(f"处理结果: {result}")
           except Exception as e:
               self.log.error(f"处理失败: {e}", exc_info=True)
               await event.reply("❌ 处理失败，请稍后重试")
   ```

2. **健康检查接口**
   ```python
   @filter.admin_only()
   @filter.command("health")
   async def health_check(self, event: BaseMessageEvent):
       status = {
           "plugin": self.name,
           "version": self.version,
           "uptime": self.get_uptime(),
           "memory_usage": self.get_memory_usage(),
           "active_users": len(self.active_users),
           "error_count": self.error_count
       }
       
       await event.reply(f"📊 插件状态:\n{json.dumps(status, indent=2)}")
   ```

#### Q13: 如何更新插件不影响服务？

**A:** 热更新和版本管理：

1. **优雅关闭**
   ```python
   class MyPlugin(BasePlugin):
       async def on_unload(self):
           """插件卸载时清理资源"""
           self.log.info(f"{self.name} 开始卸载...")
           
           # 保存数据
           self._save_data()
           
           # 清理任务
           if hasattr(self, '_background_task'):
               self._background_task.cancel()
           
           # 关闭连接
           if hasattr(self, '_db_connection'):
               await self._db_connection.close()
           
           self.log.info(f"{self.name} 卸载完成")
   ```

2. **版本兼容性**
   ```python
   class MyPlugin(BasePlugin):
       version = "2.1.0"
       min_bot_version = "4.0.0"
       
       async def on_load(self):
           # 检查兼容性
           if not self.check_compatibility():
               raise ValueError(f"插件 {self.name} 与当前Bot版本不兼容")
           
           await super().on_load()
   ```

这些解答涵盖了 FilterRegistry 使用中的大部分常见问题。如果遇到其他问题，建议查看日志文件获取更详细的错误信息。
