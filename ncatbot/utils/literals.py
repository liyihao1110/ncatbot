NAPCAT_DIR = "napcat"
INSTALL_CHECK_PATH = "install.success"
REQUEST_SUCCESS = "ok"

OFFICIAL_GROUP_MESSAGE_EVENT = "ncatbot.group_message_event"
OFFICIAL_PRIVATE_MESSAGE_EVENT = "ncatbot.private_message_event"
OFFICIAL_REQUEST_EVENT = "ncatbot.request_event"
OFFICIAL_NOTICE_EVENT = "ncatbot.notice_event"

STATUS_ONLINE = {"status": 10, "ext_status": 0, "battery_status": 0}
STATUS_Q_ME = {"status": 60, "ext_status": 0, "battery_status": 0}
STATUS_LEAVE = {"status": 30, "ext_status": 0, "battery_status": 0}
STATUS_BUSY = {"status": 50, "ext_status": 0, "battery_status": 0}
STATUS_DND = {"status": 70, "ext_status": 0, "battery_status": 0}
STATUS_HIDDEN = {"status": 40, "ext_status": 0, "battery_status": 0}
STATUS_LISTENING = {"status": 10, "ext_status": 1028, "battery_status": 0}
STATUS_LOVE_YOU = {"status": 10, "ext_status": 2006, "battery_status": 0}
STATUS_LEARNING = {"status": 10, "ext_status": 1018, "battery_status": 0}


class Status:
    在线 = {"status": 10, "ext_status": 0, "battery_status": 0}
    Q我吧 = {"status": 60, "ext_status": 0, "battery_status": 0}
    离开 = {"status": 30, "ext_status": 0, "battery_status": 0}
    忙碌 = {"status": 50, "ext_status": 0, "battery_status": 0}
    请勿打扰 = {"status": 70, "ext_status": 0, "battery_status": 0}
    隐身 = {"status": 40, "ext_status": 0, "battery_status": 0}
    听歌中 = {"status": 10, "ext_status": 1028, "battery_status": 0}
    春日限定 = {"status": 10, "ext_status": 2037, "battery_status": 0}
    一起元梦 = {"status": 10, "ext_status": 2025, "battery_status": 0}
    求星搭子 = {"status": 10, "ext_status": 2026, "battery_status": 0}
    被掏空 = {"status": 10, "ext_status": 2014, "battery_status": 0}
    今日天气 = {"status": 10, "ext_status": 1030, "battery_status": 0}
    我crash了 = {"status": 10, "ext_status": 2019, "battery_status": 0}
    爱你 = {"status": 10, "ext_status": 2006, "battery_status": 0}
    恋爱中 = {"status": 10, "ext_status": 1051, "battery_status": 0}
    好运锦鲤 = {"status": 10, "ext_status": 1071, "battery_status": 0}
    水逆退散 = {"status": 10, "ext_status": 1201, "battery_status": 0}
    嗨到飞起 = {"status": 10, "ext_status": 1056, "battery_status": 0}
    元气满满 = {"status": 10, "ext_status": 1058, "battery_status": 0}
    宝宝认证 = {"status": 10, "ext_status": 1070, "battery_status": 0}
    一言难尽 = {"status": 10, "ext_status": 1063, "battery_status": 0}
    难得糊涂 = {"status": 10, "ext_status": 2001, "battery_status": 0}
    emo中 = {"status": 10, "ext_status": 1401, "battery_status": 0}
    我太难了 = {"status": 10, "ext_status": 1062, "battery_status": 0}
    我想开了 = {"status": 10, "ext_status": 2013, "battery_status": 0}
    我没事 = {"status": 10, "ext_status": 1052, "battery_status": 0}
    想静静 = {"status": 10, "ext_status": 1061, "battery_status": 0}
    悠哉哉 = {"status": 10, "ext_status": 1059, "battery_status": 0}
    去旅行 = {"status": 10, "ext_status": 2015, "battery_status": 0}
    信号弱 = {"status": 10, "ext_status": 1011, "battery_status": 0}
    出去浪 = {"status": 10, "ext_status": 2003, "battery_status": 0}
    肝作业 = {"status": 10, "ext_status": 2012, "battery_status": 0}
    学习中 = {"status": 10, "ext_status": 1018, "battery_status": 0}
    搬砖中 = {"status": 10, "ext_status": 2023, "battery_status": 0}
    摸鱼中 = {"status": 10, "ext_status": 1300, "battery_status": 0}
    无聊中 = {"status": 10, "ext_status": 1060, "battery_status": 0}
    timi中 = {"status": 10, "ext_status": 1027, "battery_status": 0}
    睡觉中 = {"status": 10, "ext_status": 1016, "battery_status": 0}
    熬夜中 = {"status": 10, "ext_status": 1032, "battery_status": 0}
    追剧中 = {"status": 10, "ext_status": 1021, "battery_status": 0}
    我的电量 = {"status": 10, "ext_status": 1000, "battery_status": 0}


EVENT_QUEUE_MAX_SIZE = 64  # 事件队列最大长度
PLUGINS_DIR = "plugins"  # 插件目录
META_CONFIG_PATH = None  # 元数据，所有插件一份(只读)
PERSISTENT_DIR = "data"  # 插件私有数据目录
