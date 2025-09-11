## PrivateAPI 简明参考

私聊文件上传与“对方正在输入”状态控制。

统一入口：`status.global_api`。

---

### 文件
- 上传私聊文件：`upload_private_file(user_id, file, name) -> None`
- 获取私聊文件直链：`get_private_file_url(file_id) -> str`
- 多路复用发送（选择其一）：`post_private_file(user_id, image=None, record=None, video=None, file=None) -> str`
  - 仅允许传入一种媒体参数，否则抛错
  - 内部转发到 `send_private_image/record/video/file` 等

---

### 其它
- 设置输入状态：`set_input_status(status: int) -> None`
  - `0`: "对方正在说话"；`1`: "对方正在输入"

---

### 同步映射
提供 `upload_private_file_sync`、`get_private_file_url_sync`、`post_private_file_sync`、`set_input_status_sync`。

---

### 相关文档
- 事件快速回复：`docs/api/reference/Events.md`
- 消息模型与媒体段：`docs/api/MessageSegment.md`
- 通用约定：`docs/api/reference/Common.md`
