# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-21 18:27:52
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-02-21 19:47:06
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @message: 喵喵喵?
# @Copyright (c) 2025 by Fish-LP, MIT License 
# -------------------------
EVENT_QUEUE_MAX_SIZE = 64  # 事件队列最大长度
PLUGINS_DIR = "./plugins"  # 插件目录
META_CONFIG_PATH = None  # 元数据，所有插件一份(只读)
PERSISTENT_DIR = "./data"  # 插件私有数据目录

OFFICIAL_GROUP_MESSAGE_EVENT = 'napcat.group'
OFFICIAL_PRIVATE_MESSAGE_EVENT = 'napcat.private'
OFFICIAL_REQUEST_EVENT = 'napcat.request'
OFFICIAL_NOTICE_EVENT = 'napcat.notice'