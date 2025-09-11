## AccountAPI 简明参考

账号资料、好友相关、消息既读与部分杂项接口。通常这些不是日常高频，但在管理/查询时有用。

统一入口：`status.global_api`。

---

### 账号与资料
- 设置资料：`set_qq_profile(nickname, personal_note, sex: Literal["未知","男","女"]) -> None`
- 在线状态：`set_online_status(status, ext_status, battary_status) -> None`
- 头像（图片）：`set_avatar(file) -> None`（支持可上传对象，参见 Common）
- 个性签名：`set_self_longnick(longNick) -> None`
- 登录信息：`get_login_info() -> LoginInfo(nickname, user_id)`
- 运行状态：`get_status() -> dict`

---

### 好友
- 类猫友链：`get_friends_with_cat() -> list[dict]`
- 点赞：`send_like(user_id, times=1) -> None`
- 处理加好友请求：`set_friend_add_request(flag, approve, remark=None) -> None`
- 好友列表：`get_friend_list() -> list[dict]`
- 删除好友：`delete_friend(user_id, block=True, both=True) -> None`
- 备注：`set_friend_remark(user_id, remark) -> None`

---

### 消息既读
- 群：`mark_group_msg_as_read(group_id) -> None`
- 私聊：`mark_private_msg_as_read(user_id) -> None`
- 全部：`_mark_all_as_read() -> None`

---

### 其它
- 收藏：`create_collection(rawData, brief) -> None`
- 最近联系人：`get_recent_contact() -> list[dict]`
- 获取陌生人信息：`get_stranger_info(user_id) -> dict`
- 自定义表情列表：`fetch_custom_face(count=48) -> CustomFaceList(urls: list[str])`
- 用户状态：`nc_get_user_status(user_id) -> dict`
- Share 群（暂用途不明）：`AskShareGroup(group_id) -> None`

---

### 同步映射
上述方法均提供 `*_sync` 对应，例如：`get_login_info_sync()`、`set_friend_remark_sync(...)`。

---

### 相关文档
- 事件快速回复/管理：`docs/api/reference/Events.md`
- 通用约定：`docs/api/reference/Common.md`
