# 工具模块（Utils）详细规范

## 目标与功能
- 提供通用工具和辅助功能
- 实现跨模块使用的共享功能
- 提供资源管理和访问功能
- 实现日志和错误处理机制
- 提供配置管理和验证功能
- 支持网络 IO 和文件 IO 操作

## 核心组件
1. **Logger System**
   - `logger.py` 实现统一日志系统
   - 支持多级日志（DEBUG, INFO, WARNING, ERROR, CRITICAL）
   - 提供日志文件滚动和归档
   - 支持彩色终端输出
   - 实现日志钩子系统

2. **Config System**
   - `config.py` 管理全局配置
   - 支持从文件加载配置
   - 提供配置验证和标准化
   - 支持多环境配置（开发、测试、生产）
   - 管理敏感配置（如令牌和密码）

3. **File IO**
   - `file_io.py` 提供文件操作功能
   - 支持安全的文件读写
   - 实现目录操作和管理
   - 提供 YAML/JSON 文件解析
   - 支持文件监控和变更检测

4. **Network IO**
   - `network_io.py` 提供网络请求功能
   - 封装 HTTP/HTTPS 请求
   - 支持代理和超时配置
   - 提供重试机制和错误处理
   - 实现下载和上传功能

5. **Function Enhancement**
   - `function_enhance.py` 提供函数增强工具
   - 实现重试装饰器
   - 提供异步转换工具
   - 支持函数流水线处理
   - 实现并发控制机制

6. **Assets Management**
   - `assets/` 管理静态资源
   - 提供资源访问和加载接口
   - 支持资源刷新和版本管理
   - 实现资源缓存机制

7. **Optional Features**
   - `optional/` 提供可选功能组件
   - 实现非核心功能独立封装
   - 支持动态加载和卸载
   - 减少核心依赖关系

## 接口规范
- **日志接口**
   ```python
   # 获取日志记录器
   logger = get_log()
   
   # 记录不同级别日志
   logger.debug("调试信息")
   logger.info("一般信息")
   logger.warning("警告信息")
   logger.error("错误信息")
   logger.critical("严重错误")
   ```

- **配置接口**
   ```python
   # 获取全局配置
   from ncatbot.utils import config
   
   # 设置配置项
   config.set_bot_uin("123456789")
   config.set_ws_uri("ws://localhost:3001")
   
   # 加载配置文件
   config.load_config("config.yaml")
   
   # 验证配置
   config.validate_config()
   ```

- **文件操作接口**
   ```python
   # 读写文件
   content = read_file("path/to/file")
   write_file("path/to/file", content)
   
   # 解析 YAML/JSON
   data = load_yaml("config.yaml")
   data = load_json("data.json")
   
   # 操作目录
   create_directory("path/to/dir")
   files = list_directory("path/to/dir")
   ```

- **网络请求接口**
   ```python
   # 发送 HTTP 请求
   response = http_get("https://example.com", params={"key": "value"})
   response = http_post("https://example.com", data={"key": "value"})
   
   # 下载文件
   download_file("https://example.com/file", "path/to/save")
   ```

- **函数增强接口**
   ```python
   # 重试装饰器
   @retry(max_retries=3, delay=1)
   def may_fail_function():
       # 可能失败的函数
   
   # 异步运行
   await run_func_async(sync_function, *args, **kwargs)
   ```

## 常量定义
- 事件类型常量
  - `OFFICIAL_GROUP_MESSAGE_EVENT`
  - `OFFICIAL_PRIVATE_MESSAGE_EVENT`
  - `OFFICIAL_NOTICE_EVENT`
  - `OFFICIAL_REQUEST_EVENT`
  - `OFFICIAL_STARTUP_EVENT`
  - `OFFICIAL_SHUTDOWN_EVENT`
  - `OFFICIAL_HEARTBEAT_EVENT`

- 权限组常量
  - `PermissionGroup.ROOT`
  - `PermissionGroup.ADMIN`
  - `PermissionGroup.USER`

## 实现要点
- 提供良好的注释和类型提示
- 确保工具函数的可重用性和可测试性
- 实现适当的错误处理和异常机制
- 保持模块之间的低耦合性
- 遵循 Python 最佳实践和设计模式 