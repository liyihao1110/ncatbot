import asyncio
import json
import logging
import inspect
from typing import Any, Dict, List, Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# 导入 NcatBot SDK
from ncatbot.core import BotClient
from ncatbot.core.event.message_segment import MessageArray, Text

# ----------------------- 日志配置 -----------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ncatbot")

server = Server("ncatbot")


# ----------------------- 机器人客户端 -----------------------
class NcatBotClient:
    def __init__(self, bot_qq: str, admin_qq: str):
        self.bot_qq = bot_qq
        self.admin_qq = admin_qq
        self.bot = BotClient()
        self.api = None
        self.messages: List[Dict[str, Any]] = []
        self.initialized = False

    async def initialize(self):
        """初始化BotClient（同步/异步兼容）"""
        if self.initialized:
            return
        logger.info("正在初始化 NcatBot 后端连接...")

        try:
            result = self.bot.run_backend(bt_uin=self.bot_qq, root=self.admin_qq)
            if inspect.isawaitable(result):
                self.api = await result
            else:
                self.api = result

            if not self.api:
                raise RuntimeError("NcatBot API 初始化失败")

            logger.info(f"NcatBot 客户端初始化完成，QQ: {self.bot_qq}")
            self.initialized = True

        except Exception as e:
            logger.error(f"初始化 NcatBot 客户端失败: {e}")
            raise

    async def _safe_call(self, func, *args, **kwargs):
        """自动判断同步/异步函数"""
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    async def send_group_message(self, group_id: str, message: str) -> bool:
        """发送群消息"""
        try:
            if not self.api:
                await self.initialize()

            message_array = MessageArray(Text(message))
            message_id = await self._safe_call(
                self.api.post_group_array_msg, group_id, message_array
            )
            logger.info(f"机器人 {self.bot_qq} 向群 {group_id} 发送消息: {message}")

            self.messages.append(
                {
                    "type": "group",
                    "group_id": group_id,
                    "sender": self.bot_qq,
                    "message": message,
                    "message_id": message_id,
                }
            )
            return True
        except Exception as e:
            logger.error(f"发送群消息失败: {e}")
            return False

    async def send_private_message(self, user_id: str, message: str) -> bool:
        """发送私聊消息"""
        try:
            if not self.api:
                await self.initialize()

            message_array = MessageArray(Text(message))
            message_id = await self._safe_call(
                self.api.post_private_array_msg, user_id, message_array
            )
            logger.info(f"机器人 {self.bot_qq} 向用户 {user_id} 发送消息: {message}")

            self.messages.append(
                {
                    "type": "private",
                    "user_id": user_id,
                    "sender": self.bot_qq,
                    "message": message,
                    "message_id": message_id,
                }
            )
            return True
        except Exception as e:
            logger.error(f"发送私聊消息失败: {e}")
            return False

    async def get_group_list(self) -> List[Dict[str, Any]]:
        """获取群列表"""
        try:
            if not self.api:
                await self.initialize()
            groups = await self._safe_call(self.api.get_group_list)
            return [
                {
                    "group_id": str(g["group_id"]),
                    "name": g.get("group_name", "未知群名"),
                }
                for g in groups
            ]
        except Exception as e:
            logger.error(f"获取群列表失败: {e}")
            return []

    async def get_messages(
        self, message_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """仅返回缓存消息（主动发送的）"""
        if message_type:
            return [m for m in self.messages if m["type"] == message_type]
        return self.messages


# ----------------------- 初始化客户端 -----------------------


# ----------------------- MCP 接口注册 -----------------------


# ----------------------- 启动入口 -----------------------
async def main(bot_qq_, admin_qq_):
    bot_client = NcatBotClient(bot_qq=bot_qq_, admin_qq=admin_qq_)
    await bot_client.initialize()

    @server.list_resources()
    async def handle_list_resources():
        return [
            Resource(
                uri="ncatbot://messages",
                name="消息列表",
                description="获取所有消息",
                mimeType="application/json",
            ),
            Resource(
                uri="ncatbot://groups",
                name="群列表",
                description="获取所有群",
                mimeType="application/json",
            ),
        ]

    @server.read_resource()
    async def handle_read_resource(uri: str):
        if uri == "ncatbot://messages":
            return json.dumps(await bot_client.get_messages(), ensure_ascii=False)
        elif uri == "ncatbot://groups":
            return json.dumps(await bot_client.get_group_list(), ensure_ascii=False)
        else:
            raise ValueError(f"未知资源: {uri}")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(
                name="send_group_message",
                description="发送群消息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "group_id": {"type": "string"},
                        "message": {"type": "string"},
                    },
                    "required": ["group_id", "message"],
                },
            ),
            Tool(
                name="send_private_message",
                description="发送私聊消息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "message": {"type": "string"},
                    },
                    "required": ["user_id", "message"],
                },
            ),
            Tool(
                name="get_group_list",
                description="获取群列表",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_messages",
                description="获取消息列表",
                inputSchema={
                    "type": "object",
                    "properties": {"message_type": {"type": "string"}},
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, args: Optional[Dict[str, Any]]):
        try:
            if name == "send_group_message":
                ok = await bot_client.send_group_message(
                    args["group_id"], args["message"]
                )
                return [TextContent(type="text", text="success" if ok else "failed")]
            elif name == "send_private_message":
                ok = await bot_client.send_private_message(
                    args["user_id"], args["message"]
                )
                return [TextContent(type="text", text="success" if ok else "failed")]
            elif name == "get_group_list":
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            await bot_client.get_group_list(), ensure_ascii=False
                        ),
                    )
                ]
            elif name == "get_messages":
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            await bot_client.get_messages(args.get("message_type")),
                            ensure_ascii=False,
                        ),
                    )
                ]
            else:
                return [TextContent(type="text", text=f"未知工具: {name}")]
        except Exception as e:
            logger.exception(f"调用工具失败: {e}")
            return [TextContent(type="text", text=f"error: {e}")]

    async with stdio_server() as (read_stream, write_stream):
        opts = InitializationOptions(
            server_name="ncatbot",
            server_version="0.2.2",
            capabilities=server.get_capabilities(
                notification_options=NotificationOptions(), experimental_capabilities={}
            ),
        )
        await server.run(read_stream, write_stream, opts)


def start(admin_qq: str, bot_qq: str) -> None:
    """启动 NapCat-MCP 服务（阻塞直到 Ctrl-C）"""
    try:
        asyncio.run(main(admin_qq, bot_qq))
    except KeyboardInterrupt:
        logger.info("napcat.mcp 被用户中断，正常退出。")
