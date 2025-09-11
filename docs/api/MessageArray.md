## MessageArray 使用指南（构造与解析）

本页介绍消息容器 `MessageArray` 的核心概念、构造方式、解析/序列化流程、常用 API 与示例，以及合并转发消息的特殊规则与常见问题。阅读后，你应能将上游事件中的消息解析为段列表，并以编程方式构造要发送的复合消息。

## 术语与关系

- **MessageSegment**: 单个消息段的抽象基类，子类包含 `Text`、`Image`、`At`、`Face`、`Reply`、`Node`、`Forward` 等。
- **MessageArray**: 消息段列表的容器，支持从字符串（CQ 码）、`dict`、`MessageSegment`（或它们的迭代器）构造，支持追加、过滤与序列化。收发消息时，均使用 `MessageArray` 作为消息容器。
- **PlainText 与 Text**: 均表示 `type=text`。过滤时 `filter(Text)` 会同时匹配 `PlainText` 与 `Text`。
- **Node / Forward**: 合并转发相关的消息段，具备特殊的格式限制与获取内容方式。

## 构造方式

### 1) 从消息段直接构造


```python
from ncatbot.core.event.message_segment import MessageArray, Text, At, Image

# 多参数直接传入（推荐）
msg = MessageArray(Text("你好 "), At("123456"), Image(file="local.png"))

# 或传入单个列表
msg = MessageArray([Text("你好 "), At("123456"), Image(file="local.png")])

# 或使用 from_list（列表可混合 dict 与 MessageSegment）
msg = MessageArray.from_list([
    {"type": "text", "data": {"text": "你好 "}},
    At("123456"),
])
```

- Text 会自动解析 CQ 码，PlainText 不会。

### 2) 从字符串（CQ 码）构造

`MessageArray` 将字符串当作 CQ 码进行解析（支持转义）：
```python
msg = MessageArray("[CQ:image,file=img001.jpg]这是一段文本[CQ:face,id=123]")
```
解析规则要点：
- 匹配模式：`[CQ:<type>(,<k=v>...)]`；CQ 前后的普通文本会转成 `text` 段。
- HTML 实体反转义：`&amp;`→`&`，`&#91;`→`[`，`&#93;`→`]`，`&#44;`→`,`。

### 3) 追加构造

```python
msg = MessageArray()
msg.add_text("Hello ") \
   .add_at("123456") \
   .add_image("img001.jpg") \
   .add_reply("987654321")

# 操作符拼接
msg2 = MessageArray(Text("前缀 ")) + [Image(file="a.png"), At("123")] + " 后缀"
```
可用追加方法：`add_by_list`、`add_by_segment`、`add_by_dict`、`add_text`、`add_image`、`add_at`、`add_at_all`、`add_reply`。`__add__`/`__radd__` 支持与列表、`dict`、`MessageSegment`、字符串（CQ）拼接。

## 解析与序列化

### 1) 过滤与查询
```python
from ncatbot.core.event.message_segment import Text, At, Image, Face

texts  = msg.filter(Text)        # 同时包含 Text 与 PlainText
ats    = msg.filter(At)
images = msg.filter(Image)
faces  = msg.filter(Face)

# 便捷方法
msg.filter_text(); msg.filter_at(); msg.filter_image(); msg.filter_video(); msg.filter_face()

# 是否 @ 了某人（或 @全体）
mentioned = msg.is_user_at("123456")
only_direct = msg.is_user_at("123456", all_except=True)
```

## 迷你示例

```python
from ncatbot.core.event.message_segment import MessageArray, Text, At, Image

msg = MessageArray(Text("@你看这个 "), At("123456"), Image(file="./pic.png"))

msg2 = MessageArray("[CQ:image,file=img.jpg]Hello[CQ:face,id=14]")

texts = "".join([seg.text for seg in msg.filter_text()])
mentioned = msg.is_user_at("123456")
```
