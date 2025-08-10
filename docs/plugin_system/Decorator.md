# 装饰器系统

装饰器用于简化事件处理器的注册。目前支持以下装饰器:

## @register_handler

为函数注册一个事件处理器。

```python
@register_handler(event_type: str, priority: int = 0)
def handler(event: Event):
    pass
```

## @register_server

注册一个服务处理器。

```python
@register_server(addr: str)
def server(event: Event):
    # event.data 包含请求数据
    return response_data
```

服务可以通过 `request()` 方法调用:

```python
result = await plugin.request("service_addr", data)
```

## 示例

```python
class MyPlugin(BasePlugin):
    name = "my_plugin"
    version = "1.0.0"

    @register_handler("user.login")
    async def on_login(self, event):
        print(f"用户登录: {event.data}")
        
    @register_server("get_user")
    async def get_user(self, event):
        uid = event.data["uid"]
        return {"name": "test"}
```
