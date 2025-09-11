## 事件 API 参考（Events）

本页列出最常用的事件类及其“快速回复/管理/审批”方法。所有方法均提供异步与同步两种形式，后者以 `*_sync` 结尾。

- 统一入口：`from ncatbot.core.event import GroupMessageEvent, PrivateMessageEvent, RequestEvent, BaseMessageEvent`
- 全局 API：事件方法内部委托给 `ncatbot.utils.status.global_api`

---

### BaseMessageEvent（基类）
- 常见字段（从上游事件解析）：
  - `message_id: str`：消息 ID（字符串化）
  - `user_id: str`：消息发送者 QQ
  - `message: MessageArray`：消息内容容器
  - `sender: BaseSender`：发送者信息（群/私具体类型见子类）
  - `message_type: Literal["private","group"]`
  - `sub_type: str`：子类型（由子类细化）
- 快速回复（抽象，子类实现）：
  - `async reply(text: str=None, image: str=None, rtf: MessageChain=None, ...) -> str`
  - `reply_sync(...) -> str`

> 说明：`reply(...)` 默认引用当前消息（Reply），群消息的实现支持 `at=True` 参数（默认 @ 对方）。

---

### GroupMessageEvent
- 额外字段：
  - `group_id: str`、`anonymous: Optional[AnonymousMessage]`
  - `sender: GroupSender`
- 快速回复：
  - `async reply(text: str=None, image: str=None, at: bool=True, rtf: MessageChain=None) -> str`
  - `reply_sync(...) -> str`
  - 行为：默认 `at=True`，会自动 @ 发言者并附带 `Reply`。
- 管理动作：
  - 撤回当前消息：`async delete() -> None` / `delete_sync()`
  - 禁言消息发送者：`async ban(ban_duration: int=30) -> None` / `ban_sync(...)`
  - 踢出消息发送者：`async kick() -> None` / `kick_sync()`

示例：
```python
# 一行回复并@对方
await event.reply(text="收到", at=True)
# 撤回 + 禁言 60 秒
await event.delete()
await event.ban(ban_duration=60)
```

---

### PrivateMessageEvent
- 额外字段：
  - `sub_type: Literal["friend","group","other"]`
  - `sender: PrivateSender`
- 快速回复：
  - `async reply(text: str=None, image: str=None, rtf: MessageChain=None) -> str`
  - `reply_sync(...) -> str`

示例：
```python
await event.reply(text="你好")
await event.reply(image="./pic.png")
```

---

### RequestEvent（加好友/入群请求）
- 字段：
  - `request_type: Literal["friend","group"]`
  - `flag: str`：请求标识
  - `comment: str`：验证信息（commnet）
- 审批：
  - `async approve(approve: bool=True, remark: str=None, reason: str=None) -> None`
  - `approve_sync(...) -> None`
  - 参数适配：
    - 好友请求：使用 `remark`；`reason` 将被忽略并记录 warning。
    - 入群请求：使用 `reason`；`remark` 将被忽略并记录 warning。

示例：
```python
# 同意好友并备注
await event.approve(True, remark="同城-小李")
# 拒绝入群并给理由
await event.approve(False, reason="不符合入群条件")
```

---

### 同步与异步的选择
- 推荐异步：更契合插件回调与 IO 场景。
- 同步写法：如需在同步上下文中调用，使用 `*_sync` 等价方法，返回值与行为一致。

---

### 相关主题
- 消息段与容器：`docs/api/MessageSegment.md`、`docs/api/MessageArray.md`
- 合并转发：`docs/api/ForwardMessage.md`
- 进阶底层接口（发送、群管、账号）：参见 `docs/api/reference/MessageAPI.md`、`GroupAPI.md`、`AccountAPI.md`、`PrivateAPI.md`、`SupportAPI.md`
