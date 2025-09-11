## GroupAPI 简明参考

本页列出群相关的底层接口。建议优先使用事件方法处理当前消息上下文下的管理操作；本页适合跨上下文或批量操作。

统一入口：`status.global_api`（类型 `BotAPI`）。

---

### 群成员与权限管理
- 踢人：`set_group_kick(group_id, user_id, reject_add_request=False) -> None`
- 批量踢：`set_group_kick_members(group_id, user_id, reject_add_request=False) -> None`
- 禁言成员：`set_group_ban(group_id, user_id, duration=1800) -> None`
- 全员禁言：`set_group_whole_ban(group_id, enable: bool) -> None`
- 设管理员：`set_group_admin(group_id, user_id, enable: bool) -> None`
- 退群/解散：`set_group_leave(group_id, is_dismiss=False) -> None`
- 设头衔：`set_group_special_title(group_id, user_id, special_title="") -> None`
- 处理加群请求：`set_group_add_request(flag, approve: bool, reason: str=None) -> None`
- 改群名片：`set_group_card(group_id, user_id, card="") -> None`

---

### 群消息管理
- 设为精华：`set_essence_msg(message_id) -> None`
- 取消精华：`delete_essence_msg(message_id) -> None`
- 拉取精华列表：`get_group_essence_msg(group_id) -> list[dict]`

---

### 群文件
- 发送文件（按类型复用消息 API）：`post_group_file(group_id, image|record|video|file=...) -> str`
- 上传群文件：`upload_group_file(group_id, file, name, folder) -> str`
- 移动文件：`move_group_file(group_id, file_id, current_parent_directory, target_parent_directory) -> None`
- 转存永久：`trans_group_file(group_id, file_id) -> None`
- 重命名：`rename_group_file(group_id, file_id, new_name) -> None`
- 删除文件/文件夹：`delete_group_file(group_id, file_id) -> None` / `delete_group_folder(group_id, folder_id) -> None`
- 新建文件夹：`create_group_file_folder(group_id, folder_name) -> None`
- 根目录文件：`get_group_root_files(group_id, file_count=50) -> dict`
- 按文件夹：`get_group_files_by_folder(group_id, folder_id, file_count=50) -> dict`
- 获取直链：`get_group_file_url(group_id, file_id) -> str`
- 拉取文件到本地（后台下载）：`get_file(file_id, file) -> File`

---

### 群信息与荣誉
- 荣誉信息：`get_group_honor_info(group_id, type: Literal["talkative","performer","legend","emotion","all"]) -> GroupChatActivity`
- 基本信息：`get_group_info(group_id) -> GroupInfo`
- 扩展信息：`get_group_info_ex(group_id) -> dict`
- 成员信息：`get_group_member_info(group_id, user_id) -> GroupMemberInfo`
- 成员列表：`get_group_member_list(group_id) -> GroupMemberList`
- 禁言列表：`get_group_shut_list(group_id) -> GroupMemberList`
- 设群备注：`set_group_remark(group_id, remark) -> None`
- 群签到/发送签到：`set_group_sign(group_id) -> None` / `send_group_sign(group_id) -> None`
- 设群头像（仅 URL）：`set_group_avatar(group_id, file_url) -> None`
- 改群名：`set_group_name(group_id, name) -> None`
- 群公告（内部接口）：`_send_group_notice(group_id, content, confirm_required=False, image=None, is_show_edit_card=False, pinned=False) -> None`

---

### 数据类（选摘）
- `GroupInfo`: `group_id, group_name, member_count, ...`
- `GroupMemberInfo`: `user_id, nickname, role, shut_up_timestamp, ...`
- `GroupMemberList`: `members: list[GroupMemberInfo]`，并提供若干筛选方法
- `GroupChatActivity`: `current_talkative, talkative_list, performer_list, ...`

---

### 同步映射
所有方法均提供 `*_sync` 对应。

---

### 相关文档
- 事件管理动作：`docs/api/reference/Events.md`（`delete/ban/kick`）
- 消息发送与媒体：`docs/api/reference/MessageAPI.md`
- 通用约定：`docs/api/reference/Common.md`
