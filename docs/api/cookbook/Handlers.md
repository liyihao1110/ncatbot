## 处理小抄（Handlers Cookbook）

这里给出基于“事件快速回复”方法的常见场景代码片段，便于即抄即用。

---

### 群：回复并 @ 对方
```python
async def on_group(event):
    await event.reply(text="收到", at=True)
```

### 群：仅引用回复（不@）
```python
await event.reply(text="只引用", at=False)
```

### 群：撤回当前消息
```python
await event.delete()
```

### 群：禁言消息发送者 60 秒
```python
await event.ban(ban_duration=60)
```

### 群：踢出消息发送者
```python
await event.kick()
```

### 群：带图片的回复
```python
await event.reply(image="./pic.png")
```

### 私聊：快速文本/图片回复
```python
await event.reply(text="你好")
await event.reply(image="./pic.png")
```

### 请求：同意加好友并设置备注
```python
await event.approve(True, remark="来自活动 A")
```

### 请求：拒绝入群并给理由
```python
await event.approve(False, reason="请先完成实名认证")
```

---

### 同步环境用法（示例）
```python
# 群
event.reply_sync(text="OK", at=True)
event.delete_sync()
event.ban_sync(60)
event.kick_sync()

# 私聊
event.reply_sync(text="你好")

# 请求
event.approve_sync(True, remark="新同学")
```

---

### 相关文档
- 事件快速上手：`docs/api/QuickStart_Events.md`
- 事件 API 参考：`docs/api/reference/Events.md`
- 消息结构与构造：`docs/api/MessageSegment.md`、`docs/api/MessageArray.md`
- 合并转发：`docs/api/ForwardMessage.md`
