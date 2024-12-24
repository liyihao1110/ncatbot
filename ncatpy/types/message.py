import datetime

def create_group_message(payload: dict):
    group_id = payload.get('group_id')
    payload = payload.get('kwargs')
    text = payload.get('text', None)
    face = payload.get('face', None)
    image = payload.get('image', None)
    record = payload.get('record', None)
    video = payload.get('video', None)
    rps = payload.get('rps', None)
    dice = payload.get('dice', None)
    contact = payload.get('contact', None)
    file = payload.get('file', None)
    music = payload.get('music', None)

    _data = {
        "action": "send_group_msg",
        "params": {"group_id": group_id, "message": []},
        "echo": int(datetime.datetime.now().timestamp())
    }

    if text:
        _data["params"]["message"].append({"type": "text", "data": {"text": text}})
    elif face:
        _data["params"]["message"].append({"type": "face", "data": {"id": face}})
    elif image:
        if isinstance(image, str):
            _data["params"]["message"].append({"type": "image", "data": {"file": image}})
        elif isinstance(image, dict):
            _data["params"]["message"].append({"type": "image", "data": image})
        else:
            raise ValueError("image must be str or dict")
    elif record:
        _data["params"]["message"].append({"type": "record", "data": {"file": record}})
    elif video:
        if isinstance(video, str):
            _data["params"]["message"].append({"type": "video", "data": {"file": video}})
        elif isinstance(video, dict):
            _data["params"]["message"].append({"type": "video", "data": video})
        else:
            raise ValueError("video must be str or dict")
    elif rps:
        _data["params"]["message"].append({"type": "rps"})
    elif dice:
        _data["params"]["message"].append({"type": "dice"})
    elif contact:
        if isinstance(contact, dict):
            _data["params"]["message"].append({"type": "contact", "data": contact})
        else:
            raise ValueError("contact must be dict")
    elif file:
        if isinstance(file, str):
            _data["params"]["message"].append({"type": "file", "data": {"file": file}})
        elif isinstance(file, dict):
            _data["params"]["message"].append({"type": "file", "data": file})
        else:
            raise ValueError("file must be str or dict")
    elif music:
        if isinstance(music, str):
            _data["params"]["message"].append({"type": "music", "data": {"type": "qq", "id": music}})
        elif isinstance(music, dict):
            _data["params"]["message"].append({"type": "music", "data": music})
        else:
            raise ValueError("music must be str or dict")

    else:
        raise ValueError("message must be text or face or image or record or video or rps or dice or contact or file or music")

    return _data

def create_private_message(payload: dict):
    user_id = payload.get('user_id')
    payload = payload.get('kwargs')
    text = payload.get('text', None)
    face = payload.get('face', None)
    image = payload.get('image', None)
    record = payload.get('record', None)
    video = payload.get('video', None)
    rps = payload.get('rps', None)
    dice = payload.get('dice', None)
    contact = payload.get('contact', None)
    file = payload.get('file', None)
    music = payload.get('music', None)

    _data = {
        "action": "send_private_msg",
        "params": {"user_id": user_id, "message": []},
        "echo": int(datetime.datetime.now().timestamp())
    }

    if text:
        _data["params"]["message"].append({"type": "text", "data": {"text": text}})
    elif face:
        _data["params"]["message"].append({"type": "face", "data": {"id": face}})
    elif image:
        if isinstance(image, str):
            _data["params"]["message"].append({"type": "image", "data": {"file": image}})
        elif isinstance(image, dict):
            _data["params"]["message"].append({"type": "image", "data": image})
        else:
            raise ValueError("image must be str or dict")
    elif record:
        _data["params"]["message"].append({"type": "record", "data": {"file": record}})
    elif video:
        if isinstance(video, str):
            _data["params"]["message"].append({"type": "video", "data": {"file": video}})
        elif isinstance(video, dict):
            _data["params"]["message"].append({"type": "video", "data": video})
        else:
            raise ValueError("video must be str or dict")
    elif rps:
        _data["params"]["message"].append({"type": "rps"})
    elif dice:
        _data["params"]["message"].append({"type": "dice"})
    elif contact:
        if isinstance(contact, dict):
            _data["params"]["message"].append({"type": "contact", "data": contact})
        else:
            raise ValueError("contact must be dict")
    elif file:
        if isinstance(file, str):
            _data["params"]["message"].append({"type": "file", "data": {"file": file}})
        elif isinstance(file, dict):
            _data["params"]["message"].append({"type": "file", "data": file})
        else:
            raise ValueError("file must be str or dict")
    elif music:
        if isinstance(music, str):
            _data["params"]["message"].append({"type": "music", "data": {"type": "qq", "id": music}})
        elif isinstance(music, dict):
            _data["params"]["message"].append({"type": "music", "data": music})
        else:
            raise ValueError("music must be str or dict")

    else:
        raise ValueError("message must be text or face or image or record or video or rps or dice or contact or file or music")

    return _data
