import os


def read_file(file_path) -> any:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def convert_uploadable_object(i, message_type):
    """将可上传对象转换为标准格式"""
    if i.startswith("http"):
        return {"type": message_type, "data": {"file": i}}
    elif i.startswith("base64://"):
        return {"type": message_type, "data": {"file": i}}
    elif os.path.exists(i):
        return {"type": message_type, "data": {"file": f"file:///{os.path.abspath(i)}"}}
    else:
        return {"type": message_type, "data": {"file": f"file:///{i}"}}
