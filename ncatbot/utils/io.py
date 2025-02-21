import asyncio
import base64
import json
import os
import pickle
import warnings
import xml.etree.ElementTree as ET
from configparser import ConfigParser
from pathlib import Path
from typing import Any, Dict, Optional

import httpx


def read_file(file_path) -> any:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def convert_uploadable_object(i, message_type):
    """将可上传对象转换为标准格式"""
    if i.startswith("http"):
        if message_type == "image":
            try:
                with httpx.Client() as client:
                    response = client.get(i)
                    response.raise_for_status()
                    image_data = response.content
                    i = f"base64://{base64.b64encode(image_data).decode('utf-8')}"
            except httpx.HTTPError as e:
                return {"type": "text", "data": {"text": f"URL请求失败: {e}"}}
            except Exception as e:
                return {"type": "text", "data": {"text": f"图片转换失败: {e}"}}
        return {"type": message_type, "data": {"file": i}}
    elif i.startswith("base64://"):
        return {"type": message_type, "data": {"file": i}}
    elif os.path.exists(i):
        if message_type == "image":
            with open(i, "rb") as f:
                image_data = f.read()
                i = f"base64://{base64.b64encode(image_data).decode('utf-8')}"
        else:
            i = f"file:///{os.path.abspath(i)}"
        return {"type": message_type, "data": {"file": i}}
    else:
        return {"type": message_type, "data": {"file": f"file:///{i}"}}