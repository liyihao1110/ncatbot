## MessageAPI 简明参考

本页罗列底层消息发送/管理/获取接口要点。建议优先使用事件方法（见 `reference/Events.md`），此页用于进阶/跨上下文调用。

统一入口（聚合在 `BotAPI`）：
```python
from ncatbot.core.api import BotAPI
# 推荐：使用 ncatbot.utils.status.global_api
```

---

### 群聊发送
- 基础：
  - `send_group_text(group_id, text) -> str`
  - `send_group_plain_text(group_id, text) -> str`
  - `send_group_image(group_id, image) -> str`
  - `send_group_record(group_id, file) -> str`
  - `send_group_file(group_id, file, name=None) -> str`
  - `send_group_music(group_id, type: Literal["qq","163"], id) -> str`
  - `send_group_custom_music(group_id, audio, url, title, content=None, image=None) -> str`
- 组合：
  - `post_group_msg(group_id, text=None, at=None, reply=None, image=None, rtf=None) -> str`
  - `post_group_array_msg(group_id, msg: MessageArray) -> str`
- 互动：
  - `send_group_dice(group_id, value=1) -> str`
  - `send_group_rps(group_id, value=1) -> str`
- 转发：
  - `post_group_forward_msg(group_id, forward: Forward) -> str`
  - `send_group_forward_msg_by_id(group_id, messages: list[Union[str,int]]) -> str`
  - `forward_group_single_msg(group_id, message_id) -> str`

返回：message_id（字符串）。均有 `*_sync` 对应。

---

### 私聊发送
- 基础：
  - `send_private_text(user_id, text) -> str`
  - `send_private_plain_text(user_id, text) -> str`
  - `send_private_image(user_id, image) -> str`
  - `send_private_record(user_id, file) -> str`
  - `send_private_file(user_id, file, name=None) -> str`
  - `send_private_music(user_id, type, id) -> str`
  - `send_private_custom_music(user_id, audio, url, title, content=None, image=None) -> str`
- 组合：
  - `post_private_msg(user_id, text=None, reply=None, image=None, rtf=None) -> str`
  - `post_private_array_msg(user_id, msg: MessageArray) -> str`
- 互动：
  - `send_private_dice(user_id, value=1) -> str`
  - `send_private_rps(user_id, value=1) -> str`
- 转发：
  - `post_private_forward_msg(user_id, forward: Forward) -> str`
  - `send_private_forward_msg_by_id(user_id, messages: list[Union[str,int]]) -> str`
  - `forward_private_single_msg(user_id, message_id) -> str`

返回：message_id（字符串）。均有 `*_sync` 对应。

---

### 通用操作
- 撤回/删除：`delete_msg(message_id) -> None`
- 戳一戳：`send_poke(group_id=None, user_id=None) -> None`（互斥参数）
- 贴表情：`set_msg_emoji_like(message_id, emoji_id, set=True) -> None`

---

### 获取与媒体
- 历史：
  - `get_group_msg_history(group_id, message_seq, number=20, reverseOrder=False) -> list[GroupMessageEvent]`
  - `get_friend_msg_history(user_id, message_seq, number=20, reverseOrder=False) -> list[PrivateMessageEvent]`
- 单条/转发：
  - `get_msg(message_id) -> BaseMessageEvent`
  - `get_forward_msg(message_id) -> Forward`
- 媒体拉取（互斥参数二选一）：
  - `get_image(file=None, file_id=None) -> Image`
  - `get_record(file=None, file_id=None, out_format="mp3") -> Record`
- 表情贴详情：`fetch_emoji_like(message_id, emoji_id, emoji_type) -> dict`

---

### 同步映射
所有方法均提供 `*_sync` 等价版本，例如：
- `post_group_msg_sync`、`send_private_image_sync`、`delete_msg_sync`、`get_image_sync` ...

---

### 关联文档
- 事件快速回复：`docs/api/reference/Events.md`、`docs/api/QuickStart_Events.md`
- 消息模型：`docs/api/MessageSegment.md`、`docs/api/MessageArray.md`
- 合并转发：`docs/api/ForwardMessage.md`
- 通用约定：`docs/api/reference/Common.md`
