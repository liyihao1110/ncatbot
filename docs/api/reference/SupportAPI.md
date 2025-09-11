## SupportAPI 简明参考

辅助能力：AI 声聊候选、能力检查、OCR（Windows）、版本信息与退出。

统一入口：`status.global_api`。

---

### AI 声聊（实验性）
- 获取角色列表：`get_ai_characters(group_id, chat_type: Literal[1,2]) -> AICharacterList`
  - `AICharacterList.characters: list[AICharacter]`，支持 `get_search_id_by_name(name)`
- 发送并获取语音链接（可能不可用）：`get_ai_record(group_id, character_id, text) -> str`

---

### 能力检查
- 是否可发图片：`can_send_image() -> bool`
- 群是否可发语音：`can_send_record(group_id) -> bool`

---

### OCR（仅 Windows）
- 图片文字识别：`ocr_image(image) -> list[dict]`

---

### 其它
- 版本信息：`get_version_info() -> dict`
- 退出机器人：`bot_exit() -> None`

---

### 同步映射
提供 `get_ai_characters_sync`、`get_ai_record_sync`、`can_send_image_sync`、`can_send_record_sync`、`ocr_image_sync`、`get_version_info_sync`、`bot_exit_sync`。

---

### 相关文档
- 事件与快速回复：`docs/api/reference/Events.md`
- 通用约定：`docs/api/reference/Common.md`
