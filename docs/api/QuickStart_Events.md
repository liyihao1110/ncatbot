## 事件快速上手（Quick Start — Events）

本页聚焦“事件对象即入口”的最常用能力：收到消息后快速回复、常用管理操作（撤回/禁言/踢）、以及请求事件的快速处理。示例默认使用异步接口，文末附同步用法。

- 核心事件类型：`GroupMessageEvent`、`PrivateMessageEvent`、`RequestEvent`
- 快速回复：`reply(...)` / `reply_sync(...)`
- 群管动作（群消息事件专有）：`delete()`、`kick()`、`ban(seconds)`（均有 `*_sync`）
- 请求处理：`approve(approve=True, remark|reason)`（有 `approve_sync`）

---

### 收到群消息：一行回复并@对方

```python
# event: GroupMessageEvent
await event.reply(text="收到啦", at=True)  # 默认 at=True
```
- 等效底层调用：`status.global_api.post_group_msg(group_id, text, at, reply=message_id, image=None, rtf=None)`
- `at=True` 会自动 @ 发言者，同时带 `Reply`（引用当前消息）。

仅引用回复而不@：
```python
await event.reply(text="只引用不@", at=False)
```

发送图片：
```python
await event.reply(image="./pic.png")
```

撤回当前消息、禁言 60 秒、踢出：
```python
await event.delete()
await event.ban(ban_duration=60)
await event.kick()
```

---

### 收到私聊消息：快速回复

```python
# event: PrivateMessageEvent
await event.reply(text="你好")
await event.reply(image="./pic.png")
```

---

### 处理请求事件（加好友/入群）

```python
# event: RequestEvent
# 同意加好友并设置备注
await event.approve(approve=True, remark="来自群 123 的小李")

# 拒绝入群并给出理由
await event.approve(approve=False, reason="请先阅读群规再申请")
```
- `request_type == "friend"`：支持 `remark`，`reason` 会被忽略并记录 warning。
- `request_type == "group"`：支持 `reason`，`remark` 会被忽略并记录 warning。

---

### 同步接口用法

所有上述方法均提供同步版本（在方法名后加 `_sync`）。

```python
# 群消息
event.reply_sync(text="OK", at=True)
event.delete_sync()
event.ban_sync(ban_duration=30)
event.kick_sync()

# 私聊
event.reply_sync(text="你好")

# 请求
event.approve_sync(approve=True, remark="新朋友")
```

> 建议：插件/处理器以异步写法为主；如需在同步环境中调用，可使用 `*_sync` 方法。

---

### 进阶：直接使用全局 API（可选）

事件方法内部均调用全局 API（`status.global_api`）。一般不需要手写底层调用，但你可以在进阶场景使用它们：
- 群聊发送：`post_group_msg`、`post_group_array_msg`、`send_group_image` ...
- 私聊发送：`post_private_msg`、`send_private_image` ...
- 合并转发：`post_group_forward_msg`、`send_group_forward_msg_by_id` ...

有关消息段与容器，请参阅：
- `docs/api/MessageSegment.md`
- `docs/api/MessageArray.md`
- `docs/api/ForwardMessage.md`
