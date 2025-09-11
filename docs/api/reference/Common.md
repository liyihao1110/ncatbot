## 通用约定（Common）

本页汇总 API 层的通用规则：返回值与异常、参数互斥、可上传对象规范化，以及同步/异步方法的配对关系。

---

### 返回值约定
- 统一返回包：`APIReturnStatus`（`retcode==0` 视为成功）
- 消息发送返回：`MessageAPIReturnStatus.message_id`（字符串）
- 文档中如未特殊说明：
  - 管理/审批类通常 `None`（仅表示执行成功）
  - 获取类返回对应的数据对象/字典/列表（事件/媒体/群成员等）

---

### 异常
- `NapCatAPIError(info)`：当上游返回 `retcode != 0` 时抛出（会打印错误并在 debug 时输出栈）
- `ExclusiveArgumentError(a, b, extra_info)`：互斥参数校验失败（见下节）

---

### 互斥参数
- 工具函数：`check_exclusive_argument(arg1, arg2, names: list[str], error: bool=False)`
  - 两者必须“有且仅有一个”为非空；均为空或同时存在会触发异常/警告
  - 当 `error=True` 时直接抛出 `ExclusiveArgumentError`
- 典型用例：
  - `send_poke(group_id=None, user_id=None)` 需要指定其一
  - `get_record(file=None, file_id=None)` / `get_image(file=None, file_id=None)` 二选一

---

### 可上传对象的规范化
- 涉及图片/语音/视频/文件等均支持多种输入：本地路径、http(s) URL、`base64://...`、dataURI
- 规范化入口：`convert_uploadable_object`（位于 `ncatbot.core.event.message_segment.message_segment`）
- 关联文档：`docs/api/MessageSegment.md`（媒体段结构）、`docs/api/MessageArray.md`

---

### 同步与异步
- 原生方法皆为 `async`，为方便在同步环境中使用，提供 `*_sync` 对等方法（内部通过 `run_coroutine` 执行）
- 事件方法（推荐优先使用）：
  - `reply` ⇄ `reply_sync`
  - 群管：`delete/ban/kick` ⇄ `delete_sync/ban_sync/kick_sync`
  - 请求：`approve` ⇄ `approve_sync`
- 底层 API 方法：几乎均提供 `xxx` 与 `xxx_sync` 成对出现

---

### 何时直接使用底层 API
- 当事件上下文不可用或需要跨上下文操作时（例如：根据 id 对历史消息进行转发、对任意群/好友发送消息、批量文件操作）
- 常见入口：`status.global_api`（类型为 `BotAPI`，聚合了 Message/Group/Private/Account/Support）
