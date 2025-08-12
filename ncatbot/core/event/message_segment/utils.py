import re
import os
import base64
import urllib.request
from urllib.parse import urljoin
from ncatbot.utils import ncatbot_config

def convert_uploadable_object(i):
    """将可上传对象转换为标准格式"""

    def is_base64(s: str):
        if s.startswith("base64://"):
            return True
        if re.match(
            r"data:image/(jpg|jpeg|png|gif|bmp|webp|tiff|svg|mp4|avi|mov|wmv|flv|mkv|mpg|mpeg|m4v);base64,",
            s,
        ):
            return True
        return False

    def to_base64(s: str):
        if s.startswith("base64://"):
            return s
        if re.match(
            r"data:image/(jpg|jpeg|png|gif|bmp|webp|tiff|svg|mp4|avi|mov|wmv|flv|mkv|mpg|mpeg|m4v);base64,",
            s,
        ):
            m = re.match(
                r"data:image/(jpg|jpeg|png|gif|bmp|webp|tiff|svg|mp4|avi|mov|wmv|flv|mkv|mpg|mpeg|m4v);base64,(.*)",
                s,
            )
            return f"base64://{m.group(2)}"

    if i.startswith("http"):
        return i
    elif is_base64(i):
        return to_base64(i)
    elif os.path.exists(i):
        if ncatbot_config.is_napcat_local():
            return os.path.abspath(i)
        i = urljoin(
            "file:",
            f"base64://{base64.b64encode(open(i, 'rb').read()).decode('utf-8')}",
        )
        return i
    else:
        # 文件不存在时同样规范处理(可能在 NapCat 机子上)
        file_url = urljoin("file:", urllib.request.pathname2url(os.path.abspath(i)))
        return file_url