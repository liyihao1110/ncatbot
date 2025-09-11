## 合并转发消息（Forward/Node）使用指南

本文介绍合并转发消息在 ncatbot 中的解析与构造方式，覆盖核心类型 `Forward`、`Node`、`MessageArray`，以及帮助类 `ForwardConstructor` 的用法，并展示如何通过全局 API 发送合并转发消息。

### 核心概念与关系

- **MessageArray**: 消息段容器。若其中包含 `Forward` 或 `Node`，则整条消息被视为“合并转发消息”。
- **Node**: 合并转发中的“节点”，代表一条历史消息（或构造出的消息），包含 `user_id`、`nickname` 与 `content`（一个 `MessageArray`）。
- **Forward**: 合并转发主体，包含若干 `Node`，或仅有 `id`（需通过接口拉取其内容）。
- 设计约束：合并转发消息不得与其他消息段混用，否则会在 `MessageArray` 构造时抛出 `MessageFormatError`。

---

## 解析流程

### 1) 识别是否为合并转发

```python
from ncatbot.core.event.message_segment import MessageArray

msg: MessageArray = event.message
if msg.is_forward_msg():
    # 该消息为合并转发
    ...
```

### 2) 展平含有 id 的合并转发

当 `MessageArray` 中含有 `Forward` 段且仅给出 `id` 时，可通过接口展平为可遍历内容：
```python
forward = await msg.plain_forward_msg()   # type: Forward
nodes = await forward.get_content()       # list[Node]
for node in nodes:
    uid = node.user_id
    nick = node.nickname
    content = node.content                # MessageArray（普通段或继续包含转发）
```
说明：
- `plain_forward_msg()` 内部通过 `status.global_api.get_forward_msg(message_id)` 拉取并返回 `Forward` 对象。
- `Forward.get_content()` 进一步填充 `Forward.content` 并返回 `list[Node]`。

### 3) 读取节点消息内容

每个 `Node.content` 是一个 `MessageArray`，可使用常规过滤 API：
```python
from ncatbot.core.event.message_segment import Text, Image

texts = node.content.filter(Text)
images = node.content.filter(Image)
```

---

## 构造流程

### 方式一：使用 ForwardConstructor（推荐）
`ForwardConstructor` 提供便捷 API 以构造 `Forward`：
```python
from ncatbot.core.helper.forward_constructor import ForwardConstructor
from ncatbot.core.event.message_segment import Text, Image, File, Video

fcr = ForwardConstructor(user_id="123456", nickname="QQ用户")
fcr.attach_text("第一条文本")
fcr.attach_image("./pic.png")
fcr.attach_file("./report.pdf")
fcr.attach_viedo("./demo.mp4")

forward = fcr.to_forward()  # type: Forward
```
说明：
- `attach(...)` 会内部创建 `Node(user_id, nickname, content=MessageArray(...))` 并加入列表。
- 也支持 `attach_message_id(message_id)` 从历史消息生成节点、`attach_forward(forward)` 嵌套已有转发。

### 方式二：手动构造 Node 与 Forward

```python
from ncatbot.core.event.message_segment import MessageArray, Node, Forward, Text, Image

node1 = Node(user_id="123", nickname="A", content=MessageArray(Text("你好")))
node2 = Node(user_id="456", nickname="B", content=MessageArray([Text("看图"), Image("./a.png")]))
forward = Forward(content=[node1, node2])
```
也可从消息事件字典构造 `Node`（例如历史消息记录）：
```python
node = Node.from_message_event(message_event_dict)
```
或从若干消息事件/节点聚合：
```python
# messages: list[Node | MessageEventData]
forward = Forward.from_messages(messages, message_type="group")
```

> 注：`Forward.from_message_id(...)` 为异步构造历史消息的便捷方法，当前实现依赖全局 API 拉取消息；建议优先使用 `ForwardConstructor.attach_message_id(...)` 或 `api_message.send_*_forward_msg_by_id(...)` 封装。

---

## 发送合并转发

### 直接发送 `Forward`
```python
from ncatbot.utils import status

# 群聊
msg_id = await status.global_api.post_group_forward_msg(group_id, forward)

# 私聊
msg_id = await status.global_api.post_private_forward_msg(user_id, forward)
```

### 通用接口（自动判定）

```python
msg_id = await status.global_api.post_forward_msg(group_id=gid, msg=forward)
# 或 msg_id = await status.global_api.post_forward_msg(user_id=uid, msg=forward)
```

### 发送“由 id 组成”的聊天记录

若你手头只有历史消息 id 列表，可使用封装方法：
```python
# 群聊：由若干消息 id 组成
msg_id = await status.global_api.send_group_forward_msg_by_id(group_id, [mid1, mid2])

# 私聊：由若干消息 id 组成
msg_id = await status.global_api.send_private_forward_msg_by_id(user_id, [mid1, mid2])
```
此外还提供底层 `send_*_forward_msg`，直接传入 `Forward.to_forward_dict()` 的结构（`messages/news/prompt/summary/source`）。

---

## 序列化与嵌套

- `Forward.to_forward_dict()` 会将结构转换为发送端可接受的格式，并将内部 `type` 统一为 `node`，同时处理 `content/messages` 字段的兼容。
- 若 `Node.content` 内仍包含合并转发，则会被递归处理为节点结构，以满足上游适配。
- 从上游事件解析出的“带 id 的转发”，可先用 `MessageArray.plain_forward_msg()` 展平为 `Forward`，再进行二次处理或转发。

---

## 注意事项

- 合并转发消息不得与其他段混用（构造时即校验），否则抛出 `MessageFormatError`。
- `Node.content` 必须是 `MessageArray`；其摘要 `get_summary()` 通过拼接内部消息段摘要生成。
- 图片/文件/视频等可上传对象在 `to_dict()` 时将统一规范化（`convert_uploadable_object`）。
- 若需要只读浏览历史转发，优先使用 `plain_forward_msg()` + `get_content()`；若要重组并发送，推荐用 `ForwardConstructor`。

---

## 迷你示例

### 解析收到的合并转发
```python
from ncatbot.core.event.message_segment import Text

msg = event.message  # MessageArray
if msg.is_forward_msg():
    forward = await msg.plain_forward_msg()
    nodes = await forward.get_content()
    for n in nodes:
        print(n.nickname, n.user_id)
        text = "".join(seg.text for seg in n.content.filter(Text))
        print(text)
```

### 构造并发送合并转发

```python
from ncatbot.core.helper.forward_constructor import ForwardConstructor
from ncatbot.utils import status

fcr = ForwardConstructor(user_id="10086", nickname="小助手")
fcr.attach_text("你好，这是合并转发示例")
fcr.attach_image("./demo.png")
forward = fcr.to_forward()

# 发送到群
msg_id = await status.global_api.post_group_forward_msg(123456, forward)
```
