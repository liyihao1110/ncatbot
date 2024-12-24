# NcatBot

![logo](https://github.com/liyihao1110/NcatBot/blob/main/resource/logo.png?raw=true)

---

NcatBot是一个开源的基于Napcat.QQ开发的PythonSDK，使用python调用QQ。

使用简单的代码，你就可以完成一个能够处理所有信息的QQ机器人。

你还可以使用别人编写的插件！！！

#### 安装

---

可以通过本命令安装itchat：

```bash
git clone https://github.com/liyihao1110/NcatBot.git
```

#### 简单入门实例

---

首先你需要填写config.yaml文件:

```yaml
ws:
  Protocol: ws
  ip: 127.0.0.1
  port: 3001

http:
  Protocol: http
  ip: 127.0.0.1
  port: 3000

plugin:
  xunfei:
    api_url:
    api_key:
    model: generalv3.5
    personality: You are a helpful assistant.
```

然后运行以下代码：

```python
# encoding: utf-8

import ncatpy
from ncatpy import logging
from ncatpy.message import GroupMessage,PrivateMessage

_log = logging.get_logger()

class MyClient(ncatpy.Client):
    async def on_group_message(self, message: GroupMessage):
        _log.info(f"收到群消息，ID: {message.message.text.text}")
        _log.info(message.user_id)
        if message.user_id == 2793415370:
            # 当提问者的QQ号是2793415370时，调用XunfeiGPT插件回答他的问题
            t = await self._XunfeiGPT.ai_response(input=message.message.text.text, group_id = message.group_id)
            _log.info(t)

    async def on_private_message(self, message: PrivateMessage):
        _log.info(f"收到私聊消息，ID: {message.message.text.text}")
        if message.message.text.text == "你好":
            t = await self._api.send_msg(user_id=message.user_id, text="你好,o")
            _log.info(t)

if __name__ == "__main__":
    intents = ncatpy.Intents.public()
    client = MyClient(intents=intents, plugins=["XunfeiGPT"])# 如果没有插件，则不需要添加plugins=["XunfeiGPT"]
    client.run()# 只支持本地端口<-目前
```

#### 插件

---

插件是NcatBot的扩展，你可以使用别人编写的插件，也可以自己编写插件。

插件编写逻辑具体查看ncatpy/plugins/XunfeiGPT.py

编写好的插件进行pr，必须给出详细的示例和说明，目前不提供在线安装，自行安装只需要下载别人的插件，将其放入plugins文件夹即可。

此方案只是预览版！！！所有要求提在[QQ群](https://qm.qq.com/q/LSdJ4p9UOW)里面

时间有限，如果有不好的地方，欢迎提issue，或者加QQ群交流。

#### 致谢

---

[botpy](https://github.com/tencent-connect/botpy) - 一个基于 Python 的 QQ 机器人 SDK，参考了logging

[Napcat](https://github.com/NapNeko/NapCatQQ) - 现代化的基于 NTQQ 的 Bot 协议端实现
