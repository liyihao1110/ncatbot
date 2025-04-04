import os
from typing import Union

from ncatbot.adapter import Route
from ncatbot.core.element import *
from ncatbot.utils import (
    REQUEST_SUCCESS,
    Status,
    config,
    convert_uploadable_object,
    get_log,
    md_maker,
    read_file,
)

_log = get_log()


def report(func):
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        return check_and_log(result)

    return wrapper


def check_and_log(result):
    if result.get("status", None) == REQUEST_SUCCESS:
        _log.debug(result)
    else:
        _log.warning(result)
    return result


class BotAPI:
    def __init__(self):
        self._http = Route()

    async def _get_forward_msgs(self, message: dict):
        message_id = message["message_id"]
        msg = await self.get_forward_msg(message_id)
        if "messages" in msg["data"]:
            return msg["data"]["messages"]
        return message["message"][0]["data"]["content"]

    async def _message_node_construct(self, record: dict):
        data = {}

        def wash_message(msg: dict):
            # reply 报告原消息已过期是正常行为
            # TODO: 实现视频转发
            print("PROCESS:", msg)
            if msg["type"] in ["text", "at", "reply", "file"]:
                return msg
            elif msg["type"] == "face":
                return {
                    "type": "face",
                    "data": {
                        "id": msg["data"]["id"],
                    },
                }
            elif msg["type"] == "image":
                return {
                    "type": "image",
                    "data": {
                        "file": msg["data"]["url"],
                        # "url": msg["data"]["url"],
                        "summary": msg["data"].get("summary", "图片"),
                    },
                }
            elif msg["type"] == "video":
                return {"type": "text", "data": {"text": "视频"}}
                # return {
                #     "type": "video",
                #     "data": {
                #         "file": msg["data"]["file"],
                #         # "url": msg["data"]["url"],
                #         "summary": msg["data"].get("summary", "视频"),
                #     }
                # }
            elif msg["type"] == "forward":
                return None
            else:
                return None

        if "forward" in [msg["type"] for msg in record["message"]]:
            # 这应该才是正常实现, 实际上可能 NapCat 没人会写递归所以只能用下面的实现
            # data["content"] = {
            #     "type": "forward",
            #     "data": {
            #         "id": record['message'][0]['data']['content']
            #     }
            # }
            result = await self._construct_forward_message(
                (await self._get_forward_msgs(record))
            )
            data["content"] = result["messages"]
            data["summary"] = result["summary"]
            data["prompt"] = result["prompt"]
            data["news"] = result["news"]
            data["source"] = result["source"]
        else:
            data["content"] = [
                wash_message(msg)
                for msg in record["message"]
                if wash_message(msg) is not None
            ]

        data["nickname"] = record["sender"]["nickname"]
        data["user_id"] = record["sender"]["user_id"]
        node = {
            "type": "node",
            "data": data,
        }
        return node

    async def _construct_forward_message(self, messages):
        """
        :param messages: 消息列表
        :return: 转发消息
        """

        def decode_summary(rpt):
            def decode_single_message(msg):
                if msg["type"] == "text":
                    return msg["data"]["text"]
                elif msg["type"] == "image":
                    if "summary" in msg["data"] and msg["data"]["summary"] != "":
                        return msg["data"]["summary"]
                    return "[图片]"
                elif msg["type"] == "video":
                    if "summary" in msg["data"] and msg["data"]["summary"] != "":
                        return msg["data"]["summary"]
                    return "[视频]"
                elif msg["type"] == "forward":
                    return "[聊天记录]"
                elif msg["type"] == "face":
                    return msg["data"]["raw"]["faceText"]
                elif msg["type"] == "reply":
                    return ""
                elif msg["type"] == "file":
                    return f"[文件] {msg['data']['file']}"

            result = ""
            for message in rpt["message"]:
                result += decode_single_message(message)
            return result

        message_content, reports, news = [], [], []
        for msg in messages:
            report = (
                (await self.get_msg(str(msg)))["data"] if isinstance(msg, str) else msg
            )
            reports.append(report)
            node = await self._message_node_construct(report)
            if node is not None:
                message_content.append(node)
            news.append(
                {"text": report["sender"]["nickname"] + ": " + decode_summary(report)}
            )

        # 检查messages是否为空
        if not reports:
            return {
                "messages": [],
                "source": "空的聊天记录",
                "summary": "没有可查看的转发消息",
                "news": [],
                "prompt": "聊天记录",
            }

        last_report = reports[-1]

        if len(news) > 4:
            news = news[:4]

        if last_report["message_type"] == "group":
            target = "群聊"
        else:
            participants = list(
                set([record["sender"]["nickname"] for record in reports])
            )
            if len(participants) == 1:
                target = participants[0]
            else:
                assert len(participants) == 2
                target = participants[0] + "和" + participants[1]

        result = {
            "messages": message_content,
            "source": f"{target}的聊天记录",
            "summary": f"查看{len(message_content)}条转发消息",
            "news": news,
            "prompt": "聊天记录",
        }
        return result

    # ---------------------
    # region 用户接口
    # ---------------------
    @report
    async def set_qq_profile(self, nickname: str, personal_note: str, sex: str):
        """
        :param nickname: 昵称
        :param personal_note: 个性签名
        :param sex: 性别
        :return: 设置账号信息
        """
        return await self._http.post(
            "/set_qq_profile",
            {"nickname": nickname, "personal_note": personal_note, "sex": sex},
        )

    @report
    async def get_user_card(self, user_id: int, phone_number: str):
        """
        :param user_id: QQ号
        :param phone_number: 手机号
        :return: 获取用户名片
        """
        return await self._http.post(
            "/ArkSharePeer", {"user_id": user_id, "phoneNumber": phone_number}
        )

    @report
    async def get_group_card(self, group_id: int, phone_number: str):
        """
        :param group_id: 群号
        :param phone_number: 手机号
        :return: 获取群名片
        """
        return await self._http.post(
            "/ArkSharePeer", {"group_id": group_id, "phoneNumber": phone_number}
        )

    @report
    async def get_share_group_card(self, group_id: str):
        """
        :param group_id: 群号
        :return: 获取群共享名片
        """
        return await self._http.post("/ArkShareGroup", {"group_id": group_id})

    @report
    async def set_online_status(self, status: str):
        """
        :param status: 在线状态
        :return: 设置在线状态
        """
        if hasattr(Status, status):
            status = getattr(Status, status)
        return await self._http.post("/set_online_status", params=dict(status))

    @report
    async def get_friends_with_category(self):
        """
        :return: 获取好友列表
        """
        return await self._http.post("/get_friends_with_category", {})

    @report
    async def set_qq_avatar(self, avatar: str):
        """
        :param avatar: 头像路径，支持本地路径和网络路径
        :return: 设置头像
        """
        return await self._http.post("/set_qq_avatar", {"file": avatar})

    @report
    async def send_like(self, user_id: str, times: int):
        """
        :param user_id: QQ号
        :param times: 次数
        :return: 发送赞
        """
        return await self._http.post("/send_like", {"user_id": user_id, "times": times})

    @report
    async def create_collection(self, rawdata: str, brief: str):
        """
        :param rawdata: 内容
        :param brief: 标题
        :return: 创建收藏
        """
        return await self._http.post(
            "/create_collection", {"rawData": rawdata, "brief": brief}
        )

    @report
    async def set_friend_add_request(self, flag: str, approve: bool, remark: str):
        """
        :param flag: 请求ID
        :param approve: 是否同意
        :param remark: 备注
        :return: 设置好友请求
        """
        return await self._http.post(
            "/set_friend_add_request",
            {"flag": flag, "approve": approve, "remark": remark},
        )

    @report
    async def set_self_long_nick(self, longnick: str):
        """
        :param longnick: 个性签名内容
        :return: 设置个性签名
        """
        return await self._http.post("/set_self_longnick", {"longNick": longnick})

    async def get_stranger_info(self, user_id: Union[int, str]):
        """
        :param user_id: QQ号
        :return: 获取陌生人信息
        """
        return await self._http.post("/get_stranger_info", {"user_id": user_id})

    @report
    async def get_friend_list(self, cache: bool):
        """
        :param cache: 是否使用缓存
        :return: 获取好友列表
        """
        return await self._http.post("/get_friend_list", {"no_cache": cache})

    @report
    async def get_profile_like(self):
        """
        :return: 获取个人资料卡点赞数
        """
        return await self._http.post("/get_profile_like", {})

    @report
    async def fetch_custom_face(self, count: int):
        """
        :param count: 数量
        :return: 获取收藏表情
        """
        return await self._http.post("/fetch_custom_face", {"count": count})

    @report
    async def upload_private_file(self, user_id: Union[int, str], file: str, name: str):
        """
        :param user_id: QQ号
        :param file: 文件路径
        :param name: 文件名
        :return: 上传私聊文件
        """
        return await self._http.post(
            "/upload_private_file", {"user_id": user_id, "file": file, "name": name}
        )

    @report
    async def delete_friend(
        self,
        user_id: Union[int, str],
        friend_id: Union[int, str],
        temp_block: bool,
        temp_both_del: bool,
    ):
        """
        :param user_id: QQ号
        :param friend_id: 好友ID
        :param temp_block: 拉黑
        :param temp_both_del: 双向删除
        :return: 删除好友
        """
        return await self._http.post(
            "/delete_friend",
            {
                "user_id": user_id,
                "friend_id": friend_id,
                "temp_block": temp_block,
                "temp_both_del": temp_both_del,
            },
        )

    @report
    async def nc_get_user_status(self, user_id: Union[int, str]):
        """
        :param user_id: QQ号
        :return: 获取用户状态
        """
        return await self._http.post("/nc_get_user_status", {"user_id": user_id})

    @report
    async def get_mini_app_ark(self, app_json: dict):
        """
        :param app_json: 小程序JSON
        :return: 获取小程序ARK
        """
        return await self._http.post("/get_mini_app_ark", params=app_json)

    # ---------------------
    # region 消息接口
    # ---------------------

    @report
    async def mark_msg_as_read(
        self, group_id: Union[int, str] = None, user_id: Union[int, str] = None
    ):
        """
        :param group_id: 群号,二选一
        :param user_id: QQ号,二选一
        :return: 设置消息已读
        """
        if group_id:
            return await self._http.post("/mark_msg_as_read", {"group_id": group_id})
        elif user_id:
            return await self._http.post("/mark_msg_as_read", {"user_id": user_id})

    @report
    async def mark_group_msg_as_read(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 设置群聊已读
        """
        return await self._http.post("/mark_group_msg_as_read", {"group_id": group_id})

    @report
    async def mark_private_msg_as_read(self, user_id: Union[int, str]):
        """
        :param user_id: QQ号
        :return: 设置私聊已读
        """
        return await self._http.post("/mark_private_msg_as_read", {"user_id": user_id})

    @report
    async def mark_all_as_read(self):
        """
        :return: 设置所有消息已读
        """
        return await self._http.post("/_mark_all_as_read", {})

    @report
    async def delete_msg(self, message_id: Union[int, str]):
        """
        :param message_id: 消息ID
        :return: 删除消息
        """
        return await self._http.post("/delete_msg", {"message_id": message_id})

    @report
    async def get_msg(self, message_id: Union[int, str]):
        """
        :param message_id: 消息ID
        :return: 获取消息
        """
        return await self._http.post("/get_msg", {"message_id": message_id})

    @report
    async def get_image(self, image_id: str):
        """
        :param image_id: 图片ID
        :return: 获取图片消息详情
        """
        return await self._http.post("/get_image", {"file_id": image_id})

    @report
    async def get_record(self, record_id: str, output_type: str = "mp3"):
        """
        :param record_id: 语音ID
        :param output_type: 输出类型，枚举值:mp3 amr wma m4a spx ogg wav flac,默认为mp3
        :return: 获取语音消息详情
        """
        return await self._http.post(
            "/get_record", {"file_id": record_id, "out_format": output_type}
        )

    @report
    async def get_file(self, file_id: str):
        """
        :param file_id: 文件ID
        :return: 获取文件消息详情
        """
        return await self._http.post("/get_file", {"file_id": file_id})

    @report
    async def get_group_msg_history(
        self,
        group_id: Union[int, str],
        message_seq: Union[int, str],
        count: int,
        reverse_order: bool,
    ):
        """
        :param group_id: 群号
        :param message_seq: 消息序号
        :param count: 数量
        :param reverse_order: 是否倒序
        :return: 获取群消息历史记录
        """
        return await self._http.post(
            "/get_group_msg_history",
            {
                "group_id": group_id,
                "message_seq": message_seq,
                "count": count,
                "reverseOrder": reverse_order,
            },
        )

    @report
    async def set_msg_emoji_like(
        self, message_id: Union[int, str], emoji_id: int, emoji_set: bool
    ):
        """
        :param message_id: 消息ID
        :param emoji_id: 表情ID
        :param emoji_set: 设置
        :return: 设置消息表情点赞
        """
        return await self._http.post(
            "/set_msg_emoji_like",
            {"message_id": message_id, "emoji_id": emoji_id, "set": emoji_set},
        )

    @report
    async def get_friend_msg_history(
        self,
        user_id: Union[int, str],
        message_seq: Union[int, str],
        count: int,
        reverse_order: bool,
    ):
        """
        :param user_id: QQ号
        :param message_seq: 消息序号
        :param count: 数量
        :param reverse_order: 是否倒序
        :return: 获取好友消息历史记录
        """
        return await self._http.post(
            "/get_friend_msg_history",
            {
                "user_id": user_id,
                "message_seq": message_seq,
                "count": count,
                "reverseOrder": reverse_order,
            },
        )

    @report
    async def get_recent_contact(self, count: int):
        """
        获取的最新消息是每个会话最新的消息
        :param count: 会话数量
        :return: 最近消息列表
        """
        return await self._http.post("/get_recent_contact", {"count": count})

    @report
    async def fetch_emoji_like(
        self,
        message_id: Union[int, str],
        emoji_id: str,
        emoji_type: str,
        group_id: Union[int, str] = None,
        user_id: Union[int, str] = None,
        count: int = None,
    ):
        """
        :param message_id: 消息ID
        :param emoji_id: 表情ID
        :param emoji_type: 表情类型
        :param group_id: 群号,二选一
        :param user_id: QQ号,二选一
        :param count: 数量,可选
        :return: 获取贴表情详情
        """
        if group_id:
            if count:
                return await self._http.post(
                    "/fetch_emoji_like",
                    {
                        "message_id": message_id,
                        "emojiId": emoji_id,
                        "emojiType": emoji_type,
                        "group_id": group_id,
                        "count": count,
                    },
                )
            else:
                return await self._http.post(
                    "/fetch_emoji_like",
                    {
                        "message_id": message_id,
                        "emojiId": emoji_id,
                        "emojiType": emoji_type,
                        "group_id": group_id,
                    },
                )
        elif user_id:
            if count:
                return await self._http.post(
                    "/fetch_emoji_like",
                    {
                        "message_id": message_id,
                        "emojiId": emoji_id,
                        "emojiType": emoji_type,
                        "user_id": user_id,
                        "count": count,
                    },
                )
            else:
                return await self._http.post(
                    "/fetch_emoji_like",
                    {
                        "message_id": message_id,
                        "emojiId": emoji_id,
                        "emojiType": emoji_type,
                        "user_id": user_id,
                    },
                )

    @report
    async def get_forward_msg(self, message_id: str):
        """
        :param message_id: 消息ID
        :return: 获取合并转发消息
        """
        return await self._http.post("/get_forward_msg", {"message_id": message_id})

    @report
    async def send_poke(
        self, user_id: Union[int, str], group_id: Union[int, str] = None
    ):
        """
        :param user_id: QQ号
        :param group_id: 群号,可选，不填则为私聊
        :return: 发送戳一戳
        """
        if group_id:
            return await self._http.post(
                "/send_poke", {"user_id": user_id, "group_id": group_id}
            )
        else:
            return await self._http.post("/send_poke", {"user_id": user_id})

    @report
    async def forward_friend_single_msg(
        self, message_id: str, user_id: Union[int, str]
    ):
        """
        :param message_id: 消息ID
        :param user_id: 发送对象QQ号
        :return: 转发好友消息
        """
        return await self._http.post(
            "/forward_friend_single_msg", {"user_id": user_id, "message_id": message_id}
        )

    @report
    async def send_private_forward_msg(
        self, user_id: Union[int, str], messages: list[str]
    ):
        """
        :param user_id: 发送对象QQ号
        :param messages: 消息列表
        :return: 合并转发私聊消息
        """
        payload = await self._construct_forward_message(messages)
        payload["user_id"] = user_id
        return await self._http.post("/send_private_forward_msg", payload)

    # ---------------------
    # region 群组接口
    # ---------------------

    @report
    async def set_group_kick(
        self,
        group_id: Union[int, str],
        user_id: Union[int, str],
        reject_add_request: bool = False,
    ):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param reject_add_request: 是否群拉黑
        :return: 踢出群成员
        """
        return await self._http.post(
            "/set_group_kick",
            {
                "group_id": group_id,
                "user_id": user_id,
                "reject_add_request": reject_add_request,
            },
        )

    @report
    async def set_group_ban(
        self, group_id: Union[int, str], user_id: Union[int, str], duration: int
    ):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param duration: 禁言时长,单位秒,0为取消禁言
        :return: 群组禁言
        """
        return await self._http.post(
            "/set_group_ban",
            {"group_id": group_id, "user_id": user_id, "duration": duration},
        )

    @report
    async def get_group_system_msg(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群系统消息
        """
        return await self._http.post("/get_group_system_msg", {"group_id": group_id})

    @report
    async def get_essence_msg_list(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取精华消息列表
        """
        return await self._http.post("/get_essence_msg_list", {"group_id": group_id})

    @report
    async def set_group_whole_ban(self, group_id: Union[int, str], enable: bool):
        """
        :param group_id: 群号
        :param enable: 是否禁言
        :return: 群组全员禁言
        """
        return await self._http.post(
            "/set_group_whole_ban", {"group_id": group_id, "enable": enable}
        )

    @report
    async def set_group_portrait(self, group_id: Union[int, str], file: str):
        """
        :param group_id: 群号
        :param file: 文件路径,支持网络路径和本地路径
        :return: 设置群头像
        """
        return await self._http.post(
            "/set_group_portrait", {"group_id": group_id, "file": file}
        )

    @report
    async def set_group_admin(
        self, group_id: Union[int, str], user_id: Union[int, str], enable: bool
    ):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param enable: 是否设置为管理
        :return: 设置群管理员
        """
        return await self._http.post(
            "/set_group_admin",
            {"group_id": group_id, "user_id": user_id, "enable": enable},
        )

    @report
    async def set_essence_msg(self, message_id: Union[int, str]):
        """
        :param message_id: 消息ID
        :return: 设置精华消息
        """
        return await self._http.post("/set_essence_msg", {"message_id": message_id})

    @report
    async def set_group_card(
        self, group_id: Union[int, str], user_id: Union[int, str], card: str
    ):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param card: 群名片,为空则为取消群名片
        :return: 设置群名片
        """
        return await self._http.post(
            "/set_group_card", {"group_id": group_id, "user_id": user_id, "card": card}
        )

    @report
    async def delete_essence_msg(self, message_id: Union[int, str]):
        """
        :param message_id: 消息ID
        :return: 删除精华消息
        """
        return await self._http.post("/delete_essence_msg", {"message_id": message_id})

    @report
    async def set_group_name(self, group_id: Union[int, str], group_name: str):
        """
        :param group_id: 群号
        :param group_name: 群名
        :return: 设置群名
        """
        return await self._http.post(
            "/set_group_name", {"group_id": group_id, "group_name": group_name}
        )

    @report
    async def set_group_leave(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 退出群组
        """
        return await self._http.post("/set_group_leave", {"group_id": group_id})

    @report
    async def send_group_notice(
        self, group_id: Union[int, str], content: str, image: str = None
    ):
        """
        :param group_id: 群号
        :param content: 内容
        :param image: 图片路径，可选
        :return: 发送群公告
        """
        if image:
            return await self._http.post(
                "/_send_group_notice",
                {"group_id": group_id, "content": content, "image": image},
            )
        else:
            return await self._http.post(
                "/_send_group_notice", {"group_id": group_id, "content": content}
            )

    @report
    async def get_group_notice(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群公告
        """
        return await self._http.post("/_get_group_notice", {"group_id": group_id})

    @report
    async def set_group_special_title(
        self, group_id: Union[int, str], user_id: Union[int, str], special_title: str
    ):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param special_title: 群头衔
        :return: 设置群头衔
        """
        return await self._http.post(
            "/set_group_special_title",
            {"group_id": group_id, "user_id": user_id, "special_title": special_title},
        )

    @report
    async def upload_group_file(
        self, group_id: Union[int, str], file: str, name: str, folder_id: str
    ):
        """
        :param group_id: 群号
        :param file: 文件路径
        :param name: 文件名
        :param folder_id: 文件夹ID
        :return: 上传群文件
        """
        return await self._http.post(
            "/upload_group_file",
            {"group_id": group_id, "file": file, "name": name, "folder_id": folder_id},
        )

    @report
    async def set_group_add_request(self, flag: str, approve: bool, reason: str = None):
        """
        :param flag: 请求flag
        :param approve: 是否同意
        :param reason: 拒绝理由
        :return: 处理加群请求
        """
        if approve:
            return await self._http.post(
                "/set_group_add_request", {"flag": flag, "approve": approve}
            )
        else:
            return await self._http.post(
                "/set_group_add_request",
                {"flag": flag, "approve": approve, "reason": reason},
            )

    @report
    async def get_group_info(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群信息
        """
        return await self._http.post("/get_group_info", {"group_id": group_id})

    @report
    async def get_group_info_ex(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群信息(拓展)
        """
        return await self._http.post("/get_group_info_ex", {"group_id": group_id})

    @report
    async def create_group_file_folder(
        self, group_id: Union[int, str], folder_name: str
    ):
        """
        :param group_id: 群号
        :param folder_name: 文件夹名
        :return: 创建群文件文件夹
        """
        return await self._http.post(
            "/create_group_file_folder",
            {"group_id": group_id, "folder_name": folder_name},
        )

    @report
    async def delete_group_file(self, group_id: Union[int, str], file_id: str):
        """
        :param group_id: 群号
        :param file_id: 文件ID
        :return: 删除群文件
        """
        return await self._http.post(
            "/delete_group_file", {"group_id": group_id, "file_id": file_id}
        )

    @report
    async def delete_group_folder(self, group_id: Union[int, str], folder_id: str):
        """
        :param group_id: 群号
        :param folder_id: 文件夹ID
        :return: 删除群文件文件夹
        """
        return await self._http.post(
            "/delete_group_folder", {"group_id": group_id, "folder_id": folder_id}
        )

    @report
    async def get_group_file_system_info(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群文件系统信息
        """
        return await self._http.post(
            "/get_group_file_system_info", {"group_id": group_id}
        )

    @report
    async def get_group_root_files(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群根目录文件列表
        """
        return await self._http.post("/get_group_root_files", {"group_id": group_id})

    @report
    async def get_group_files_by_folder(
        self, group_id: Union[int, str], folder_id: str, file_count: int
    ):
        """
        :param group_id: 群号
        :param folder_id: 文件夹ID
        :param file_count: 文件数量
        :return: 获取群文件列表
        """
        return await self._http.post(
            "/get_group_files_by_folder",
            {"group_id": group_id, "folder_id": folder_id, "file_count": file_count},
        )

    @report
    async def get_group_file_url(self, group_id: Union[int, str], file_id: str):
        """
        :param group_id: 群号
        :param file_id: 文件ID
        :return: 获取群文件URL
        """
        return await self._http.post(
            "/get_group_file_url", {"group_id": group_id, "file_id": file_id}
        )

    @report
    async def get_group_list(self, no_cache: bool = False):
        """
        :param no_cache: 不缓存，默认为false
        :return: 获取群列表
        """
        return await self._http.post("/get_group_list", {"no_cache": no_cache})

    @report
    async def get_group_member_info(
        self, group_id: Union[int, str], user_id: Union[int, str], no_cache: bool
    ):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param no_cache: 不缓存
        :return: 获取群成员信息
        """
        return await self._http.post(
            "/get_group_member_info",
            {"group_id": group_id, "user_id": user_id, "no_cache": no_cache},
        )

    @report
    async def get_group_member_list(
        self, group_id: Union[int, str], no_cache: bool = False
    ):
        """
        :param group_id: 群号
        :param no_cache: 不缓存
        :return: 获取群成员列表
        """
        return await self._http.post(
            "/get_group_member_list", {"group_id": group_id, "no_cache": no_cache}
        )

    @report
    async def get_group_honor_info(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群荣誉信息
        """
        return await self._http.post("/get_group_honor_info", {"group_id": group_id})

    @report
    async def get_group_at_all_remain(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群 @全体成员 剩余次数
        """
        return await self._http.post("/get_group_at_all_remain", {"group_id": group_id})

    @report
    async def get_group_ignored_notifies(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群过滤系统消息
        """
        return await self._http.post(
            "/get_group_ignored_notifies", {"group_id": group_id}
        )

    @report
    async def set_group_sign(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 群打卡
        """
        return await self._http.post("/set_group_sign", {"group_id": group_id})

    @report
    async def send_group_sign(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 群打卡
        """
        return await self._http.post("/send_group_sign", {"group_id": group_id})

    @report
    async def get_ai_characters(
        self, group_id: Union[int, str], chat_type: Union[int, str]
    ):
        """
        :param group_id: 群号
        :param chat_type: 聊天类型
        :return: 获取AI语音人物
        """
        return await self._http.post(
            "/get_ai_characters", {"group_id": group_id, "chat_type": chat_type}
        )

    @report
    async def send_group_ai_record(
        self, group_id: Union[int, str], character: str, text: str
    ):
        """
        :param group_id: 群号
        :param character: AI语音人物,即character_id
        :param text: 文本
        :return: 发送群AI语音
        """
        return await self._http.post(
            "/send_group_ai_record",
            {"group_id": group_id, "character": character, "text": text},
        )

    @report
    async def get_ai_record(self, group_id: Union[int, str], character: str, text: str):
        """
        :param group_id: 群号
        :param character: AI语音人物,即character_id
        :param text: 文本
        :return: 获取AI语音
        """
        return await self._http.post(
            "/get_ai_record",
            {"group_id": group_id, "character": character, "text": text},
        )

    @report
    async def forward_group_single_msg(
        self, message_id: str, group_id: Union[int, str]
    ):
        """
        :param message_id: 消息ID
        :param group_id: 群号
        :return: 转发群聊消息
        """
        return await self._http.post(
            "/forward_group_single_msg",
            {"group_id": group_id, "message_id": message_id},
        )

    @report
    async def send_group_forward_msg(
        self, group_id: Union[int, str], messages: list[str]
    ):
        """
        :param group_id: 群号
        :param messages: 消息列表
        :return: 合并转发的群聊消息
        """
        if len(messages) == 0:
            return None

        payload = await self._construct_forward_message(messages)
        payload["group_id"] = group_id

        return await self._http.post("/send_private_forward_msg", payload)

    # ---------------------
    # region 系统接口
    # ---------------------

    @report
    async def get_client_key(self):
        """
        :return: 获取client_key
        """
        return await self._http.post("/get_clientkey", {})

    @report
    async def get_robot_uin_range(self):
        """
        :return: 获取机器人QQ号范围
        """
        return await self._http.post("/get_robot_uin_range", {})

    @report
    async def ocr_image(self, image: str):
        """
        :param image: 图片路径，支持本地路径和网络路径
        :return: OCR 图片识别
        """
        return await self._http.post("/ocr_image", {"image": image})

    @report
    async def ocr_image_new(self, image: str):
        """
        :param image: 图片路径，支持本地路径和网络路径
        :return: OCR 图片识别
        """
        return await self._http.post("/.ocr_image", {"image": image})

    @report
    async def translate_en2zh(self, words: list):
        """
        :param words: 待翻译的单词列表
        :return: 英文翻译为中文
        """
        return await self._http.post("/translate_en2zh", {"words": words})

    @report
    async def get_login_info(self):
        """
        :return: 获取登录号信息
        """
        return await self._http.post("/get_login_info", {})

    @report
    async def set_input_status(self, event_type: int, user_id: Union[int, str]):
        """
        :param event_type: 状态类型
        :param user_id: QQ号
        :return: 设置输入状态
        """
        return await self._http.post(
            "/set_input_status", {"eventType": event_type, "user_id": user_id}
        )

    @report
    async def download_file(
        self,
        thread_count: int,
        headers: Union[dict, str],
        base64: str = None,
        url: str = None,
        name: str = None,
    ):
        """
        :param thread_count: 下载线程数
        :param headers: 请求头
        :param base64: base64编码的图片,二选一
        :param url: 图片url,二选一
        :param name: 文件名
        :return: 下载文件
        """
        if base64:
            if name:
                return await self._http.post(
                    "/download_file",
                    {
                        "thread_count": thread_count,
                        "headers": headers,
                        "base64": base64,
                        "name": name,
                    },
                )
            else:
                return await self._http.post(
                    "/download_file",
                    {
                        "thread_count": thread_count,
                        "headers": headers,
                        "base64": base64,
                    },
                )
        elif url:
            if name:
                return await self._http.post(
                    "/download_file",
                    {
                        "thread_count": thread_count,
                        "headers": headers,
                        "url": url,
                        "name": name,
                    },
                )
            else:
                return await self._http.post(
                    "/download_file",
                    {"thread_count": thread_count, "headers": headers, "url": url},
                )

    @report
    async def get_cookies(self, domain: str):
        """
        :param domain: 域名
        :return: 获取cookies
        """
        return await self._http.post("/get_cookies", {"domain": domain})

    @report
    async def handle_quick_operation(self, context: dict, operation: dict):
        """
        :param context: 事件数据对象
        :param operation: 快速操作对象
        :return: 对事件执行快速操作
        """
        return await self._http.post(
            "/.handle_quick_operation", {"context": context, "operation": operation}
        )

    @report
    async def get_csrf_token(self):
        """
        :return: 获取 CSRF Token
        """
        return await self._http.post("/get_csrf_token", {})

    @report
    async def del_group_notice(self, group_id: Union[int, str], notice_id: str):
        """
        :param group_id: 群号
        :param notice_id: 通知ID
        :return: 删除群公告
        """
        return await self._http.post(
            "/_del_group_notice", {"group_id": group_id, "notice_id": notice_id}
        )

    @report
    async def get_credentials(self, domain: str):
        """
        :param domain: 域名
        :return: 获取 QQ 相关接口凭证
        """
        return await self._http.post("/get_credentials", {"domain": domain})

    @report
    async def get_model_show(self, model: str):
        """
        :param model: 模型名
        :return: 获取模型显示
        """
        return await self._http.post("/_get_model_show", {"model": model})

    @report
    async def can_send_image(self):
        """
        :return: 检查是否可以发送图片
        """
        return await self._http.post("/can_send_image", {})

    @report
    async def nc_get_packet_status(self):
        """
        :return: 获取packet状态
        """
        return await self._http.post("/nc_get_packet_status", {})

    @report
    async def can_send_record(self):
        """
        :return: 检查是否可以发送语音
        """
        return await self._http.post("/can_send_record", {})

    @report
    async def get_status(self):
        """
        :return: 获取状态
        """
        return await self._http.post("/get_status", {})

    @report
    async def nc_get_rkey(self):
        """
        :return: 获取rkey
        """
        return await self._http.post("/nc_get_rkey", {})

    @report
    async def get_version_info(self):
        """
        :return: 获取版本信息
        """
        return await self._http.post("/get_version_info", {})

    @report
    async def get_group_shut_list(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群禁言列表
        """
        return await self._http.post("/get_group_shut_list", {"group_id": group_id})

    @report
    async def post_group_msg(
        self,
        group_id: Union[int, str],
        text: str = None,
        face: int = None,
        jsond: str = None,
        markdown: str = None,
        at: Union[int, str] = None,
        reply: Union[int, str] = None,
        music: Union[list, dict] = None,
        dice: bool = False,
        rps: bool = False,
        image: str = None,
        rtf: MessageChain = None,
    ):
        """
        :param group_id: 群号
        :param text: 文本
        :param face: 表情
        :param jsond: JSON
        :param markdown: Markdown
        :param at: at
        :param reply: 回复
        :param music: 音乐
        :param dice: 骰子
        :param rps: 猜拳
        :param image: 图片
        :param rtf: 富文本(消息链)
        :return: 发送群消息
        """
        message: list = []
        if text:
            message.append(Text(text))
        if face:
            message.append(Face(face))
        if jsond:
            message.append(Json(jsond))
        if markdown:
            message.append(convert_uploadable_object(await md_maker(markdown), "image"))
        if at:
            message.append(At(at))
        if reply:
            message.insert(0, Reply(reply))
        if music:
            if isinstance(music, list):
                message.append(Music(music[0], music[1]))
            elif isinstance(music, dict):
                message.append(CustomMusic(**music))
        if dice:
            message.append(Dice())
        if rps:
            message.append(Rps())
        if image:
            message.append(Image(image))
        if rtf:
            # 首先检查是否有 reply，只取第一个
            reply_elem = None
            for elem in rtf.elements:
                if elem["type"] == "reply":
                    reply_elem = Reply(elem["data"]["id"])
                    break

            # 如果有 reply，插入到消息开头
            if reply_elem:
                message.insert(0, reply_elem)

            # 检查是否包含基本元素(at/图片/文本/表情/猜拳/骰子)
            basic_types = {"at", "image", "text", "face", "dice", "rps"}
            basic_elems = [elem for elem in rtf.elements if elem["type"] in basic_types]

            if basic_elems:  # 如果存在基本元素
                # 只添加基本元素
                message.extend(basic_elems)
            else:
                # 如果没有基本元素，才使用所有非reply元素
                message.extend(
                    [elem for elem in rtf.elements if elem["type"] != "reply"]
                )
        if not message:
            return {"code": 0, "msg": "消息不能为空"}
        params = {"group_id": group_id, "message": message}
        return await self._http.post("/send_group_msg", json=params)

    @report
    async def post_private_msg(
        self,
        user_id: Union[int, str],
        text: str = None,
        face: int = None,
        json: str = None,
        markdown: str = None,
        reply: Union[int, str] = None,
        music: Union[list, dict] = None,
        dice: bool = False,
        rps: bool = False,
        image: str = None,
        rtf: MessageChain = None,
    ):
        """
        :param user_id: QQ号
        :param text: 文本
        :param face: 表情
        :param json: JSON
        :param markdown: Markdown
        :param reply: 回复
        :param music: 音乐
        :param dice: 骰子
        :param rps: 猜拳
        :param image: 图片
        :param rtf: 富文本(消息链)
        :return: 发送私聊消息
        """
        message: list = []
        if text:
            message.append(Text(text))
        if face:
            message.append(Face(face))
        if json:
            message.append(Json(json))
        if markdown:
            message.append(convert_uploadable_object(await md_maker(markdown), "image"))
        if reply:
            message.insert(0, Reply(reply))
        if music:
            if isinstance(music, list):
                message.append(Music(music[0], music[1]))
            elif isinstance(music, dict):
                message.append(CustomMusic(**music))
        if dice:
            message.append(Dice())
        if rps:
            message.append(Rps())
        if image:
            message.append(Image(image))
        if rtf:
            # 首先检查是否有 reply，只取第一个
            reply_elem = None
            for elem in rtf.elements:
                if elem["type"] == "reply":
                    reply_elem = Reply(elem["data"]["id"])
                    break

            # 如果有 reply，插入到消息开头
            if reply_elem:
                message.insert(0, reply_elem)

            # 检查是否包含基本元素(图片/文本/表情/猜拳/骰子)
            basic_types = {"image", "text", "face", "dice", "rps"}
            basic_elems = [elem for elem in rtf.elements if elem["type"] in basic_types]

            if basic_elems:  # 如果存在基本元素
                # 只添加基本元素
                message.extend(basic_elems)
            else:
                # 如果没有基本元素，才使用所有非reply/at元素
                message.extend(
                    [
                        elem
                        for elem in rtf.elements
                        if elem["type"] != "reply" or elem["type"] != "at"
                    ]
                )
        if not message:
            return {"code": 0, "msg": "消息不能为空"}
        params = {"user_id": user_id, "message": message}
        return await self._http.post("/send_private_msg", json=params)

    @report
    async def post_group_file(
        self,
        group_id: Union[int, str],
        image: str = None,
        record: str = None,
        video: str = None,
        file: str = None,
        markdown: str = None,
    ):
        """
        :param group_id: 群号
        :param image: 图片
        :param record: 语音
        :param video: 视频
        :param file: 文件
        :param markdown: Markdown
        :return: 发送群文件
        """
        message: list = []

        if image:
            message.append(Image(image))
        elif record:
            message.append(Record(record))
        elif video:
            message.append(Video(video))
        elif file:
            message.append(File(file))
        elif markdown:
            message.append(
                convert_uploadable_object(
                    await md_maker(
                        read_file(
                            markdown
                            if os.path.isabs(markdown)
                            else os.path.join(os.getcwd(), markdown)
                        )
                    ),
                    "image",
                )
            )
        else:
            return {"code": 0, "msg": "请至少选择一种文件"}

        params = {"group_id": group_id, "message": message}
        return await self._http.post("/send_group_msg", json=params)

    @report
    async def post_private_file(
        self,
        user_id: Union[int, str],
        image: str = None,
        record: str = None,
        video: str = None,
        file: str = None,
        markdown: str = None,
    ):
        """
        :param user_id: QQ号
        :param image: 图片
        :param record: 语音
        :param video: 视频
        :param file: 文件
        :param markdown: Markdown
        :return: 发送私聊文件
        """
        message: list = []

        if image:
            message.append(Image(image))
        elif record:
            message.append(Record(record))
        elif video:
            message.append(Video(video))
        elif file:
            message.append(File(file))
        elif markdown:
            message.append(
                convert_uploadable_object(
                    await md_maker(
                        read_file(
                            markdown
                            if os.path.isabs(markdown)
                            else os.path.join(os.getcwd(), markdown)
                        )
                    ),
                    "image",
                )
            )
        else:
            return {"code": 0, "msg": "请至少选择一种文件"}

        params = {"user_id": user_id, "message": message}
        return await self._http.post("/send_private_msg", json=params)

    # ---------------------
    # region ncatbot扩展接口
    # ---------------------

    @report
    async def send_qqmail_text(
        self,
        receiver: str,
        token: str,
        subject: str,
        content: str,
        sender: str = f"{config.bt_uin}@qq.com" if config.bt_uin else "",
    ):
        """发送QQ邮箱文本
        :param sender: 发送者QQ邮箱
        :param receiver: 接收者QQ邮箱
        :param token: QQ邮箱授权码
        :param subject: 邮件主题
        :param content: 邮件内容
        :return: 发送结果
        """
        import smtplib
        from email.mime.text import MIMEText

        smtp_server = "smtp.qq.com"
        port = 465
        msg = MIMEText(content, "plain", "utf-8")
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = subject

        server = None  # 初始化server变量为None
        try:
            server = smtplib.SMTP_SSL(smtp_server, port)
            server.login(sender, token)
            server.sendmail(sender, [receiver], msg.as_string())
            return {"code": 0, "msg": "发送成功"}
        except Exception as e:
            return {"code": 0, "msg": str(e)}
        finally:
            if server:  # 只有server存在时才调用quit方法
                server.quit()
