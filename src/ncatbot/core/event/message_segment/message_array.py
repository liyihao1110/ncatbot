from typing import Literal, Optional, Dict, Any
from ncatbot.core.event.message_segment.message_segment import MessageSegment
from .message_segment import (
    Text,
    PlainText,
    Face,
    Image,
    File,
    Record,
    Video,
    At,
    AtAll,
    Rps,
    Dice,
    Shake,
    Poke,
    Anonymous,
    Share,
    Contact,
    Location,
    Music,
    Reply,
    Node,
    Forward,
    XML,
    Json,
)

class MessageArray():
    messages: list[MessageSegment] = []
    
    def __init__(self, data: list[Dict[str, Any]]):
        self.messages = []
        for item in data:
            if not isinstance(item, dict) or "type" not in item:
                continue
                
            msg_type = item["type"]
            msg_data = item.get("data", {})
            
            try:
                if msg_type == "text":
                    self.messages.append(PlainText(msg_data.get("text", "")))
                elif msg_type == "face":
                    self.messages.append(Face(msg_data.get("id", "")))
                elif msg_type == "image":
                    if "file" in msg_data:
                        self.messages.append(Image(msg_data["file"]))
                elif msg_type == "file":
                    file_msg = File(msg_data.get("file", ""))
                    if "type" in msg_data:
                        file_msg.data["type"] = msg_data["type"]
                    self.messages.append(file_msg)
                elif msg_type == "record":
                    record_msg = Record(msg_data.get("file", ""))
                    if "magic" in msg_data:
                        record_msg.data["magic"] = msg_data["magic"]
                    self.messages.append(record_msg)
                elif msg_type == "video":
                    if "file" in msg_data:
                        self.messages.append(Video(msg_data["file"]))
                elif msg_type == "at":
                    if "qq" in msg_data:
                        self.messages.append(At(msg_data["qq"]))
                elif msg_type == "rps":
                    self.messages.append(Rps())
                elif msg_type == "dice":
                    self.messages.append(Dice())
                elif msg_type == "shake":
                    self.messages.append(Shake())
                elif msg_type == "poke":
                    if "type" in msg_data and "id" in msg_data:
                        self.messages.append(Poke(msg_data["type"], msg_data["id"]))
                elif msg_type == "anonymous":
                    self.messages.append(Anonymous())
                elif msg_type == "share":
                    if all(k in msg_data for k in ["url", "title", "content", "image"]):
                        self.messages.append(Share(
                            msg_data["url"],
                            msg_data["title"],
                            msg_data["content"],
                            msg_data["image"]
                        ))
                elif msg_type == "contact":
                    if "type" in msg_data and "id" in msg_data:
                        self.messages.append(Contact(
                            msg_data["type"],
                            msg_data["id"]
                        ))
                elif msg_type == "location":
                    if all(k in msg_data for k in ["lat", "lon", "title", "content"]):
                        self.messages.append(Location(
                            msg_data["lat"],
                            msg_data["lon"],
                            msg_data["title"],
                            msg_data["content"]
                        ))
                elif msg_type == "music":
                    if "type" in msg_data:
                        if msg_data["type"] == "custom":
                            if all(k in msg_data for k in ["url", "title", "content", "image"]):
                                self.messages.append(Music(
                                    "custom",
                                    "",
                                    msg_data["url"],
                                    msg_data["title"],
                                    msg_data["content"],
                                    msg_data["image"]
                                ))
                        elif "id" in msg_data:
                            self.messages.append(Music(
                                msg_data["type"],
                                msg_data["id"],
                                "", "", "", ""
                            ))
                elif msg_type == "reply":
                    if "id" in msg_data:
                        self.messages.append(Reply(msg_data["id"]))
                elif msg_type == "node":
                    if all(k in msg_data for k in ["id", "user_id", "nickname"]):
                        self.messages.append(Node(
                            msg_data["id"],
                            msg_data["user_id"],
                            msg_data["nickname"]
                        ))
                elif msg_type == "forward":
                    if "id" in msg_data:
                        self.messages.append(Forward(msg_data["id"]))
                elif msg_type == "xml":
                    if "data" in msg_data:
                        self.messages.append(XML(msg_data["data"]))
                elif msg_type == "json":
                    if "data" in msg_data:
                        self.messages.append(Json(msg_data["data"]))
            except Exception as e:
                # Log error if needed
                continue
                
    def __iter__(self):
        return self.messages.__iter__()
    
    def __len__(self):
        return len(self.messages)
        
