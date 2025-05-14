# 核心模块（Core Module）详细规范

## 目标与功能
- 提供 NAPCAT 机器人框架的核心功能，负责与 NAPCAT 服务通信并提供高级 API
- 管理机器人实例的生命周期，包括初始化、启动、消息处理和终止
- 配置插件无关的系统参数（ROOT 权限、通信端口等）
- 维护与 NAPCAT 服务的 WebSocket 连接
- 解析 NAPCAT 上报的消息事件，将其转换为标准化的消息元素对象

## 核心组件
1. **Bot Manager**
   - `BotClient` 类负责管理 Bot 实例的生命周期
   - 支持阻塞和非阻塞启动模式
   - 监听和处理 NAPCAT 服务发送的各类消息（群聊、私聊、通知等）
   - 支持优雅退出和清理操作
   - 负责将消息事件转发至插件系统的 EventBus

2. **消息处理模块（Message Module）**
   - `BaseMessage`、`GroupMessage`、`PrivateMessage` 类处理不同类型的消息
   - 使用标准化的 `MessageElement` 类处理消息元素，收发消息均使用相同的对象结构
   - `MessageChain` 将多个 `MessageElement` 元素组合成完整消息
   - 提供消息构建器接口，简化消息创建和操作
   - 将 NAPCAT 上报的原始 JSON 消息数据解析为 `MessageElement` 对象

3. **消息元素模块（MessageElement Module）**
   - `MessageElement` 作为所有消息元素的基类
   - 实现各种具体的消息元素类型：
     - `Text`: 纯文本内容
     - `Image`: 图片元素，支持多种来源（URL、本地文件、Base64）
     - `At`: @用户元素
     - `AtAll`: @全体成员元素
     - `Reply`: 引用回复元素
     - `Face`: 表情元素
     - `Voice`: 语音元素
     - `Video`: 视频元素
     - `File`: 文件元素
     - 其他自定义元素类型
   - 提供元素序列化与反序列化机制
   - 支持消息元素的链式操作和组合

4. **API 模块（API Module）**
   - `BotAPI` 提供与 NAPCAT 通信的高级接口
   - 实现发送消息、获取信息、管理群组等功能
   - 对底层 HTTP/WebSocket 请求进行封装
   - 支持使用 `MessageElement` 构建和发送消息

5. **Request 模块**
   - 处理 QQ 好友请求、群组邀请等事件
   - 提供接受/拒绝的功能接口
   - 将请求事件通过 EventBus 上报给插件系统

6. **Notice 模块**
   - 处理群成员变动、文件上传等通知事件
   - 提供标准化的事件处理接口
   - 将通知事件通过 EventBus 上报给插件系统

7. **Config Manager**
   - 管理 Bot 核心配置（QQ 号、通信地址等）
   - 支持配置验证和标准化
   - 支持从文件加载配置
   - 作为实例在系统各组件间传递，避免使用全局变量

## 接口规范
- **事件系统接口**
   ```python
   # 装饰器接口
   @bot.group_event(types=["text"])
   def handle_group_message(msg):
       # 处理群消息

   @bot.private_event(types=["image"])
   def handle_private_message(msg):
       # 处理私聊消息

   @bot.notice_event()
   def handle_notice(notice):
       # 处理通知事件

   @bot.request_event()
   def handle_request(request):
       # 处理请求事件
   ```

- **消息元素接口**
   ```python
   # 创建消息链
   chain = MessageChain([
       Text("你好世界"),
       Image(url="https://example.com/image.jpg"),
       At(user_id="123456789")
   ])
   
   # 回复消息
   message.reply(MessageChain([Text("这是回复")]))
   
   # 链式操作
   chain = MessageChain().text("你好").image("path/to/image.jpg").at("123456789")
   
   # 解析接收到的消息
   for element in message.chain:
       if isinstance(element, Text):
           print(f"文本内容: {element.text}")
       elif isinstance(element, Image):
           print(f"图片URL: {element.url}")
   ```

- **启动与初始化接口**
   ```python
   # 阻塞式启动
   api = bot.run_blocking()

   # 非阻塞式启动
   api = bot.run_non_blocking()

   # 退出
   bot.exit_()
   ```

- **与插件系统的交互接口**
   - 通过插件系统提供的 EventBus 将事件传递给插件系统
   - 支持事件的异步发布和订阅
   - 事件发布示例：
     ```python
     # 发布群消息事件到插件系统
     await plugin_system.event_bus.publish_async(
         Event(
             OFFICIAL_GROUP_MESSAGE_EVENT,
             msg,
             EventSource(msg.user_id, msg.group_id)
         )
     )
     ```
   - 启动时向插件系统传递 BotAPI 和配置
   - 支持事件分发与逻辑解耦

## 配置项
- 机器人 QQ 号 (`bt_uin`)
- WebSocket 通信地址 (`ws_uri`) 和令牌 (`ws_token`)
- WebUI 地址 (`webui_uri`) 和令牌 (`webui_token`)
- ROOT 用户 QQ 号 (`root`)
- 远程模式设置 (`remote_mode`)
- 调试选项 (`debug`, `suppress_client_initial_error`)
- 消息元素处理选项 (`message_element_cache_size`, `enable_element_validation`) 