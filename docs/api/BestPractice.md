## 最佳实践

### 获取消息中的文本

```python
from ncatbot.core.event import GroupMessageEvent
from ncatbot.plugin_system import on_message

@on_message
def on_group_message(event: BaseMessageEvent):
    first_text = event.message.filter_text()[0].text # 第一段文本
    all_text = "".join(seg.text for seg in event.message.filter_text()) # 所有文本
    if "测试" in first_text:
        event.reply("前端：测试成功")

```