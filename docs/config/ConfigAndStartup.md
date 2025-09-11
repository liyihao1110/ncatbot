## 配置与启动（Config & Startup）

本页介绍 NcatBot 的配置来源、覆盖优先级、`config.yaml` 字段说明、运行时参数（StartArgs）、以及安全与远程模式注意事项。

---

### 常用配置项介绍：

- `bt_uin`：机器人 QQ 号
- `root`：管理员 QQ 号
- `ws_uri`：NapCat WebSocket 服务地址，如果为远程地址，会自动以远程模式运行。
- `ws_token`：WebSocket 令牌，如果监听公网，强制必须为强口令。
- `ws_listen_ip`：WS 监听 IP，如果监听公网，需要设置为 `0.0.0.0`。

### 在运行时设置配置项

```python
from ncatbot.core import BotClient
bot = BotClient()
# bot.run_backend(), bot.ru() 等用于启动的函数都支持这种方式。
bot.run_frontend(
    bt_uin="123456",
    ws_uri="ws://127.0.0.1:3001",
    ws_token="strong-token-Here!42",
    debug=True,
)
```

### 配置来源与覆盖顺序

1) 文件：`config.yaml`（默认路径：工作目录下，或通过环境变量覆盖）
2) ncatbot_config 的有关方法（如 `set_ws_uri`）或 `ncatbot_config.update_config(...)`（4xx 版本已经弃用，仅作兼容支持）
3) 运行时：`BotClient.run_frontend/run_backend(startArgs...)` 传入的启动参数（会写入全局配置）

环境变量：
- `NCATBOT_CONFIG_PATH`：指定配置文件路径。未设置时默认读取当前工作目录下的 `config.yaml`。

---

### config.yaml 字段说明（示例同仓库默认）

```yaml

root: '123456'                  # 管理员 QQ 号
bt_uin: '123456'                # 机器人 QQ 号
enable_webui_interaction: false # 启用 WebUI 交互式登录/引导
check_ncatbot_update: true      # 启动时检查 NcatBot 更新
skip_ncatbot_install_check: false
debug: false                    # 调试模式（打印更多堆栈/日志）

napcat:
  ws_uri: ws://localhost:3001   # NapCat WebSocket 服务地址
  webui_uri: http://localhost:6099 # NapCat WebUI 地址
  webui_token: napcat           # WebUI 令牌
  ws_token: '1234'              # WebSocket 令牌
  ws_listen_ip: localhost       # WS 监听 IP（安全校验相关）
  remote_mode: false            # 远程模式（不在本机运行 NapCat）
  check_napcat_update: false
  stop_napcat: false
  report_self_message: false
  report_forward_message_detail: true # 上报解析合并转发消息

plugin:
  plugins_dir: plugins          # 插件目录
  skip_plugin_load: false       # 跳过外部插件加载（仅加载内置插件）
  # plugin_whitelist:           # 可选：白名单
  #   - ExamplePlugin
  # plugin_blacklist:           # 可选：黑名单
```

### 快速检查清单

- 是否正确设置了 `bt_uin` / `root`？
- `ws_uri`、`ws_token` 与远端 NapCat 的配置是否一致？
- 若监听公网（`0.0.0.0`），token 是否满足强口令要求？
- 插件目录是否存在（默认自动创建）且包含你的插件？
- 启动模式选择正确（前台/后台），并按需使用同步或异步接口？
