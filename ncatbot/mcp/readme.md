# napcat MCP协议使用教程

napcat支持MCP，MCP协议可以让大语言模型使用一些方法，从而实现函数的调用。napcat现在的MCP协议复用了现有的端口，让你的机器人可以被大语言模型控制，同时可以让你的大模型读取QQ群中或是私聊列表中的消息。

## MCP协议配置教程
### 初始配置
首先，确保你的python中含有napcat的和mcp的包，想必看到这个文档，你一定已经配置好了napcat，因此这里不再赘述，详情请见napcat的主要文档。如果您没有mcp相关的包，可以在命令行中输入以下命令：
```javascript
pip install mcp
```
来使用mcp相关的函数。
### QQ号配置
打开mcp文件夹，在文件夹中找到main.py文件找到以下代码：
```javascript
bot_client = NcatBotClient(bot_qq="#填写机器人QQ号", admin_qq="#填写管理员QQ号")
```
将双引号中带井号的文字改为对应的QQ号即可，可以在代码编辑界面使用CTRL+F搜索这一段文字。并在文件夹中找到config.yaml文件中找到以下代码：
```javascript
root: '管理员QQ号'
bt_uin: '机器人QQ号'
```
并重复上述操作。
### MCP配置
在支持MCP的大语言模型中配置你的MCP工具，这里以Claude desktop为例进行演示，在左上角找到三条横线的位置，单击后点击files->settings->Developer->edit config，此时会跳转到配置界面，为json格式，此时在mcp文件夹中找到MCPconfig.json,将
```javascript
"args": ["C:\\Users\\Alex\\Desktop\\ncatbot\\main.py"],
```
其中的路径改为你此时MCP文件夹中的main.py的绝对路径即可，绝对路径可以通过右键“属性”找到。
### 注意事项
需要注意的是ncatbot MCP必须要在机器人正在运行的时候使用，单个MCP程序无法独自启动QQbot。同时目前只支持收发文字信息，还不支持表情包，图片的识别。

