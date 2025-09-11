## MessageSegment 各类型构造与结构

本页汇总 `MessageSegment` 及其子类的构造方式与序列化结构（`to_dict` 结果）。所有消息段在发送前都会被序列化为如下统一格式：

- 统一结构：`{"type": <msg_seg_type>, "data": { ...字段... }}`
- 容器：请配合 `MessageArray` 使用（见 `docs/api/MessageArray.md`），消息由若干段顺序组成。
- 可上传对象（图片/文件/视频等）的路径会被规范化（http(s)、base64、dataURI、本地路径等），见 `convert_uploadable_object`。

---

### 常用属性访问

- 点语法（推荐）：直接访问字段，更安全直观。
- 字典式访问（兼容层）：`seg["type"]` / `seg["data"]...`，基于 `to_dict()` 的快照；修改仅作用于内部缓存，不会同步到对象字段，谨慎使用。
- 摘要：`seg.get_summary()` 返回该段的简短预览字符串。
- 下载（媒体类）：`await image.download_to(dir, name=None)` 将远程/本地资源保存到指定目录，目录不存在会报错。

示例：
```python
from ncatbot.core.event.message_segment import Text, At, Image, Reply, Node

# Text / PlainText
seg = Text("你好")
print(seg.text)                # 点语法
print(seg.to_dict()["data"]["text"])  # 字典式（不推荐修改）
print(seg.get_summary())

# At / AtAll
at = At("123456")
print(at.qq)                   # "123456"

# Image / File / Video / Record
img = Image("./pic.png")
print(img.file)                # 源输入，序列化时会规范化
# 下载（需在异步环境）
# path = await img.download_to("./downloads", name="pic.png")

# Reply（id 已字符串化）
rep = Reply(987654321)
print(rep.id)                  # "987654321"

# Node（合并转发节点）
# user_id, nickname, content(=MessageArray)
print(node.user_id, node.nickname)
for part in node.content.filter_text():
    print(part.text)
```

---

### 文本类

#### Text（默认文本，支持 CQ 转义）

```python
from ncatbot.core.event.message_segment import Text
seg = Text("你好")
seg.to_dict() == {"type": "text", "data": {"text": "你好"}}
```

- `Text.text`: 文本内容

#### PlainText（纯文本，不做 CQ 转义）

```python
from ncatbot.core.event.message_segment import PlainText
seg = PlainText("[CQ:face,id=14]")  # 保留原样
seg.to_dict() == {"type": "text", "data": {"text": "[CQ:face,id=14]"}}
```

- `PlainText.text`: 文本内容

---

### 提及类

#### At（@指定用户）与 AtAll（@全体）

```python
from ncatbot.core.event.message_segment import At, AtAll
seg1 = At("123456")
seg1.to_dict() == {"type": "at", "data": {"qq": "123456"}}

seg2 = AtAll()
seg2.to_dict() == {"type": "at", "data": {"qq": "all"}}
```

- `At.qq`: 提及的用户 ID，如果为 `"all"`，则为一条 @全体成员。
- `AtAll.qq`: `all`

---

### 表情类

#### Face（QQ 表情）
```python
from ncatbot.core.event.message_segment import Face
seg = Face(14)
seg.to_dict() == {"type": "face", "data": {"id": "14", "faceText": "[表情]"}}
```

- `Face.id` 参考[QQ表情消息](https://github.com/kyubotics/coolq-http-api/wiki/%E8%A1%A8%E6%83%85-CQ-%E7%A0%81-ID-%E8%A1%A8)。
- `Face.faceText` 可从上游附带，用于摘要展示。

---

### 媒体类（可下载/上传）

均继承 `DownloadableMessageSegment`，字段 `file` 会被标准化（http(s)、base64、dataURI、本地路径）。

支持本地路径、http(s) 链接、base64、dataURI。

提供下载方法：`await seg.download_to(dir, name=None)`。

#### Image（图片）

```python
from ncatbot.core.event.message_segment import Image
seg = Image("./pic.png")
seg.to_dict() == {"type": "image", "data": {"file": "<标准化路径>"}}
# 可选：data.type == "flash" 表示闪照
```

- `Image.file`: 图片路径
- `Image.file_name`: 图片文件名（尽力提供）
- `Image.url`: 图片链接

#### Record（语音）

```python
from ncatbot.core.event.message_segment import Record
seg = Record("./voice.silk")
seg.to_dict() == {"type": "record", "data": {"file": "<标准化路径>"}}
```

- `Record.file`: 语音路径
- `Record.file_name`: 语音文件名（尽力提供）
- `Record.url`: 语音链接

#### Video（视频）

```python
from ncatbot.core.event.message_segment import Video
seg = Video("./demo.mp4")
seg.to_dict() == {"type": "video", "data": {"file": "<标准化路径>"}}
```

- `Video.file`: 视频路径
- `Video.file_name`: 视频文件名（尽力提供）
- `Video.url`: 视频链接

#### File（通用文件）

```python
from ncatbot.core.event.message_segment import File
seg = File("./report.pdf")
# to_dict 会补充文件名（name）
seg.to_dict() == {"type": "file", "data": {"file": "<标准化路径>", "name": "report.pdf"}}
```

- `File.file`: 文件路径
- `File.file_name`: 文件文件名（尽力提供）
- `File.url`: 文件链接

---

### 分享类

#### Share（链接分享）

```python
from ncatbot.core.event.message_segment import Share
seg = Share(url="https://example.com", title="分享", content="示例", image="./cover.png")
seg.to_dict() == {
  "type": "share",
  "data": {"url": "https://example.com", "title": "分享", "content": "示例", "image": "<标准化路径>"}
}
```

---

### 联系类

#### Contact（名片）
```python
# 结构示例（目前实现为简单数据承载）
{"type": "contact", "data": {"type": "qq" | "group", "id": "123456"}}
```

---

### 位置类

#### Location（位置）
```python
from ncatbot.core.event.message_segment import Location
seg = Location(lat=39.9, lon=116.4, title="天安门", content="北京")
seg.to_dict() == {
  "type": "location",
  "data": {"lat": 39.9, "lon": 116.4, "title": "天安门", "content": "北京"}
}
```

---

### 音乐类

#### Music（音乐卡片）

```python
from ncatbot.core.event.message_segment import Music
# 平台曲库（qq/163）：仅需要 id
seg1 = Music("qq", id=12345, url=None, title=None)
# 自定义卡片（custom）：需提供 url/title，可选 content/image
seg2 = Music("custom", id=0, url="https://song/1", title="歌名", content="简介", image="./cover.jpg")
# 序列化示例（custom）：
seg2.to_dict() == {
  "type": "music",
  "data": {"type": "custom", "url": "https://song/1", "title": "歌名", "content": "简介", "image": "<标准化路径>"}
}
```

---

### 回复类

#### Reply（引用回复）

```python
from ncatbot.core.event.message_segment import Reply
seg = Reply(987654321)
seg.to_dict() == {"type": "reply", "data": {"id": "987654321"}}
```

- `Reply.id`: 回复的消息 ID

---

### 合并转发相关

#### Node（转发节点）

```python
from ncatbot.core.event.message_segment import Node, MessageArray, Text
seg = Node(user_id="10086", nickname="小助手", content=MessageArray(Text("你好")))
# content 会被序列化为内部段列表
seg.to_dict() == {
  "type": "node",
  "data": {"user_id": "10086", "nickname": "小助手", "content": [{"type": "text", "data": {"text": "你好"}}]}
}
```

- `Node.user_id`: 用户 ID
- `Node.nickname`: 用户昵称
- `Node.content`: 消息内容（MessageArray）

#### Forward（合并转发）

```python
from ncatbot.core.event.message_segment import Forward, Node, MessageArray, Text
node = Node("10086", "小助手", MessageArray(Text("Hi")))
seg = Forward(content=[node])
# 或仅携带 id（需要 get_forward_msg 展平获取内容）
# seg = Forward(id="<msg_id>")

# 序列化（简化示例）：
seg.to_dict() == {
  "type": "forward",
  "data": {"content": [ {"type": "node", "data": {"user_id": "10086", "nickname": "小助手", "content": [ ... ]}} ]}
}
```
> 详细的合并转发解析与发送请参阅 `docs/api/ForwardMessage.md`。

- `Forward.id`: 转发消息 ID
- `Forward.content`: 消息内容（list[Node]）
- `Forward.message_type`: 消息类型（group/friend）

---

### 互动类

#### Rps（猜拳）、Dice（骰子）、Shake（窗口抖动）、Poke（戳一戳）、Anonymous（匿名）

```python
from ncatbot.core.event.message_segment import Rps, Dice, Shake, Poke, Anonymous
Rps().to_dict() == {"type": "rps", "data": {}}
Dice().to_dict() == {"type": "dice", "data": {}}
Shake().to_dict() == {"type": "shake", "data": {}}
Poke("123").to_dict() == {"type": "poke", "data": {"id": "123", "type": None}}
Anonymous().to_dict() == {"type": "anonymous", "data": {}}
```

---

### 结构化内容

#### XML、Json、Markdown
```python
from ncatbot.core.event.message_segment import XML, Json, Markdown
XML("<xml/>").to_dict() == {"type": "xml", "data": {"data": "<xml/>"}}
Json("{\"k\":1}").to_dict() == {"type": "json", "data": {"data": "{\"k\":1}"}}
Markdown("**bold**").to_dict() == {"type": "markdown", "data": {"content": "**bold**"}}
```

---

### 小贴士
- 仅当 `MessageArray` 全部由 `Forward`/`Node` 组成时才算合并转发；与其他段混用会报错。
- 传入本地路径时，若 NapCat 与机器人在同一机器上，路径会被转换为绝对路径；否则会转为 `base64://...` 或 `file:` URL。
- `Text` 与 `PlainText` 均为 `type=text`，`filter(Text)` 会同时匹配两者。
