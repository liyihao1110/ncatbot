# UnifiedRegistry 模式介绍图

本页用多种 Mermaid 图展示 UnifiedRegistry 的核心模块关系、事件处理流与关键数据结构，便于快速理解整体架构与交互边界。

---

## 高层组件关系（Component）

```mermaid
flowchart LR
    EB[EventBus 事件] --> URP[UnifiedRegistryPlugin]

    URP --> MP[MessagePreprocessor\n前缀/大小写/切分]
    MP --> MT[MessageTokenizer\n消息混合分词]
    MT --> ST[StringTokenizer\n字符串词法]
    MT --> PC[ParsedCommand]

    URP --> CR[CommandResolver\n命令解析]
    CR --> REG[ModernRegistry / command_registry]
    REG --> CG[CommandGroup]
    REG --> SPEC[CommandSpec / OptionSpec / ParameterSpec / OptionGroupSpec]

    URP --> FV[FilterValidator\n过滤器校验]
    FV --> FR[FilterRegistry / filter_registry]
    FR --> FE[FilterEntry + 装饰器元数据]

    URP --> AB[ArgumentBinder\n参数绑定]
    AB --> FA[FuncAnalyser\n函数签名解析]
    AB --> SPEC

    CR -->|命令已定位| AB
    FV -->|通过| EXEC[执行插件命令函数]
    AB -->|绑定后的参数/选项| EXEC

    URP --> HS[HelpGenerator / ErrorHandler]
    HS -.-> EXEC
```

要点：
- 事件由 `EventBus` 分发到 `UnifiedRegistryPlugin`，随后按“预处理 → 分词 → 解析 → 过滤 → 绑定 → 执行”的主链路推进。
- 命令与过滤器均通过注册表统一管理：`command_registry` 与 `filter_registry`。
- 帮助与错误处理贯穿各阶段，确保良好的开发与使用体验。

---

## 消息到执行的时序（Sequence）

```mermaid
sequenceDiagram
    participant User as 用户
    participant EventBus as EventBus
    participant Plugin as UnifiedRegistryPlugin
    participant Pre as MessagePreprocessor
    participant Tok as MessageTokenizer
    participant Res as CommandResolver
    participant Fil as FilterValidator
    participant Bind as ArgumentBinder
    participant Exec as 插件命令函数

    User->>EventBus: 发送消息
    EventBus->>Plugin: 分发事件
    Plugin->>Pre: 前缀与基础预处理
    Pre-->>Plugin: 预处理结果
    Plugin->>Tok: 解析混合消息（文本/图片/@ 等）
    Tok-->>Plugin: ParsedCommand
    Plugin->>Res: 解析命令与子命令
    Res-->>Plugin: CommandSpec / 目标处理函数
    Plugin->>Fil: 校验过滤器（群聊/私聊/权限等）
    Fil-->>Plugin: 通过/拒绝
    Plugin->>Bind: 绑定参数与选项（类型转换）
    Bind-->>Plugin: 实参列表/关键字参数
    Plugin->>Exec: 调用目标命令函数
    Exec-->>Plugin: 执行结果
    Plugin-->>EventBus: 回复/后续操作
```

---

## 命令注册结构（Class Diagram）

```mermaid
classDiagram
    class ModernRegistry {
      +register_command()
      +get_command()
      +get_all_aliases()
    }
    class CommandGroup {
      +name
      +aliases
      +subgroups
      +commands
    }
    class CommandSpec {
      +name
      +description
      +parameters
      +options
      +option_groups
      +filters
      +handler
    }
    class ParameterSpec
    class OptionSpec
    class OptionGroupSpec

    ModernRegistry --> CommandGroup
    CommandGroup --> CommandSpec
    CommandSpec --> ParameterSpec
    CommandSpec --> OptionSpec
    CommandSpec --> OptionGroupSpec
```

装饰器生态（示例）：
- `@command_registry.command("name", description=...)`
- `@option("-v", "--verbose", help=...)`
- `@param("target", type=..., help=...)`

---

## 过滤器系统结构（Class Diagram）

```mermaid
classDiagram
    class FilterRegistry {
      +register()
      +validate()
    }
    class FilterEntry {
      +name
      +validator
      +metadata
    }
    FilterRegistry o--> FilterEntry
```

典型过滤器：
- 群聊限定、私聊限定、管理员权限、自定义复合过滤器等。

---

## 关键关系与扩展点

- 统一注册：`UnifiedRegistryPlugin` 组合使用 `filter_registry` 与 `command_registry`，并将触发引擎延迟到首次消息时初始化，降低启动成本。
- 可扩展性：
  - 新增命令：通过 `ModernRegistry` 及装饰器完成注册。
  - 新增过滤器：向 `FilterRegistry` 注册 `FilterEntry` 并在命令上附加。
  - 新增参数类型：扩展类型转换器与绑定逻辑，`ArgumentBinder` 会统一接入。


