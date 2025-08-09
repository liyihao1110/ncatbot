# 事件系统

事件系统是插件之间通信的核心机制。它基于发布/订阅模式工作。

## 事件总线接口

插件可以通过 `BasePlugin` 基类访问以下事件总线接口:

### 发布事件

```python
async def publish(self, event_type: str, data: Any) -> List[Any]:
    """发布一个事件
  
    Args:
        event_type: 事件类型字符串
        data: 事件数据
      
    Returns:
        处理器返回值列表
    """
```

### 注册事件处理器

```python
def register_handler(self, event_type: str, handler: callable, priority: int = 0) -> UUID:
    """注册事件处理器
  
    Args:
        event_type: 要监听的事件类型
        handler: 事件处理函数
        priority: 优先级,数值越大优先级越高
      
    Returns:
        处理器ID
    """
```

### 注销处理器

```python
def unregister_handler(self, handler_id: UUID) -> bool:
    """注销单个处理器"""

def unregister_all_handler(self) -> None:
    """注销该插件的所有处理器"""
```

### 发送请求

```python
async def request(self, addr: str, data: dict = None) -> Any:
    """发送请求并等待响应
  
    Args:
        addr: 请求地址(@register_server注册的服务)
        data: 请求数据
  
    Returns:
        第一个响应结果
    """
```

## 事件类型

事件类型是一个字符串,可以是:

- 精确匹配: `"user.login"`
- 正则匹配: `"re:user\..*"`

## 示例

```python
# 发布事件
await self.publish("user.login", {"uid": 123})

# 注册处理器
@register_handler("user.login")
async def on_login(event):
    uid = event.data["uid"]
    print(f"用户 {uid} 登录")
```
