"""触发引擎（简化版 command_system）

职责：
- 首次使用时构建并冻结命令分发表（含严格前缀冲突检测）
- 运行期编排：前置检查 → 解析 → 解析命令 → 绑定参数 → 过滤校验 → 执行
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple, Any, TYPE_CHECKING
import asyncio

from ncatbot.utils import get_log

from ..registry import UnifiedRegistry  # 类型提示
from ..filter_system import FilterValidator
from ..command_system.lexer.tokenizer import StringTokenizer, Token, TokenType

from .preprocessor import MessagePreprocessor, PreprocessResult
from .resolver import CommandResolver, CommandEntry
from .binder import ArgumentBinder, BindResult

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent
    from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin


LOG = get_log(__name__)


class TriggerEngine:
    """简化命令触发引擎
    
    说明：
    - 严格禁止命令路径前缀冲突（可通过配置开启层级命令，但默认关闭）
    - 当同一函数同时被 command 与 filter 装饰时，以 command 流程为准；
      该函数不出现在“纯过滤器函数”扫描列表中，但命中后仍执行过滤器校验。
    """

    def __init__(self, 
                 registry: UnifiedRegistry,
                 plugin: "NcatBotPlugin",
                 *,
                 require_prefix: bool = True,
                 prefixes: Optional[List[str]] = None,
                 case_sensitive: bool = False,
                 allow_hierarchical: bool = False,
                 unknown_command_silent: bool = True,
                 enable_filter_scan_when_no_command: bool = True) -> None:
        self.registry = registry
        self.plugin = plugin
        self.require_prefix = require_prefix
        self.prefixes = prefixes or ["/", "!"]
        self.case_sensitive = case_sensitive
        self.allow_hierarchical = allow_hierarchical
        self.unknown_command_silent = unknown_command_silent
        self.enable_filter_scan_when_no_command = enable_filter_scan_when_no_command

        self._validator: Optional[FilterValidator] = getattr(self.registry, "_filter_validator", None)

        # 构建期只读缓存
        self._resolver = CommandResolver(
            case_sensitive=self.case_sensitive,
            allow_hierarchical=self.allow_hierarchical,
        )
        self._preprocessor = MessagePreprocessor(
            require_prefix=self.require_prefix,
            prefixes=self.prefixes,
            case_sensitive=self.case_sensitive,
        )
        self._binder = ArgumentBinder()

        self._initialized = False

    def _normalize_case(self, s: str) -> str:
        return s if self.case_sensitive else s.lower()

    def initialize_if_needed(self) -> None:
        """首次触发时构建命令分发表并做严格冲突检测。"""
        if self._initialized:
            return

        # 1) 检查消息级前缀集合冲突
        norm_prefixes = [self._normalize_case(p) for p in self.prefixes]
        for i, p1 in enumerate(norm_prefixes):
            for j, p2 in enumerate(norm_prefixes):
                if i == j:
                    continue
                if p2.startswith(p1):
                    # 严格：前缀包含不允许（例如 '!' 与 '!!'）
                    LOG.error(f"消息前缀冲突: '{p1}' 与 '{p2}' 存在包含关系")
                    raise ValueError(f"prefix conflict: {p1} vs {p2}")

        # 2) 采集命令定义（仅带 __is_command__ 的函数）
        # CommandGroup.get_all_commands 返回 {path_tuple: func}
        command_map = self.registry.get_all_commands()
        alias_map = self.registry.get_all_aliases()

        # 过滤：仅保留被标记为命令的函数（装饰器会设置 __is_command__）
        filtered_commands: Dict[Tuple[str, ...], Callable] = {}
        for path, func in command_map.items():
            if getattr(func, "__is_command__", False):
                filtered_commands[path] = func

        filtered_aliases: Dict[Tuple[str, ...], Callable] = {}
        for path, func in alias_map.items():
            if getattr(func, "__is_command__", False):
                filtered_aliases[path] = func

        # 3) 交给 resolver 构建并做冲突检测
        self._resolver.build_index(filtered_commands, filtered_aliases)

        self._initialized = True
        LOG.info(f"TriggerEngine 初始化完成：命令={len(filtered_commands)}, 别名={len(filtered_aliases)}")

    async def handle_message_event(self, event: "BaseMessageEvent") -> bool:
        """处理消息事件。返回是否已处理。"""
        # 惰性初始化
        self.initialize_if_needed()

        # 前置检查与提取首段文本（用于前缀与命令词匹配）
        pre: Optional[PreprocessResult] = self._preprocessor.precheck(event)
        if pre is None:
            # 不符合前置条件（例如不要求前缀但为空/非文本）
            return False

        # 解析首段文本为 token（用于命令匹配）
        text = pre.command_text
        tokenizer = StringTokenizer(text)
        tokens: List[Token] = tokenizer.tokenize()

        # 从首段 token 流解析命令（严格无前缀冲突则应唯一）
        match = self._resolver.resolve_from_tokens(tokens)
        if match is None:
            # 未命中命令：执行“纯过滤器函数”扫描（可配置）
            if self.enable_filter_scan_when_no_command:
                await self._run_pure_filters(event)
            return False

        func = match.func
        ignore_words = match.path_words  # 用于参数绑定的 ignore 计数

        # 参数绑定：复用 FuncAnalyser 约束
        bind_result: BindResult = self._binder.bind(func, event, ignore_words)
        if not bind_result.ok:
            # 绑定失败：可选择静默或提示（最小实现为静默）
            LOG.debug(f"参数绑定失败: {bind_result.message}")
            return False

        # 过滤器校验（命令命中后才执行过滤器）
        if self._validator is not None:
            if not self._validator.validate_filters(func, event):
                return False

        # 执行函数（注入插件实例作为 self）
        try:
            plugin = self._find_plugin_for_function(func)
            args = bind_result.args
            if plugin:
                args = (plugin, event, *args)
            else:
                args = (event, *args)

            if asyncio.iscoroutinefunction(func):
                await func(*args)
            else:
                func(*args)
            return True
        except Exception as e:
            LOG.error(f"执行命令函数失败: {func.__name__}, 错误: {e}")
            return False

    async def _run_pure_filters(self, event: "BaseMessageEvent") -> None:
        """遍历执行纯过滤器函数（不含命令函数）。"""
        for func in self.registry.filter_functions:
            # 额外防御：若误标记，仍跳过命令函数
            if getattr(func, "__is_command__", False):
                continue
            if self._validator is not None and not self._validator.validate_filters(func, event):
                continue
            try:
                plugin = self._find_plugin_for_function(func)
                if asyncio.iscoroutinefunction(func):
                    if plugin:
                        await func(plugin, event)
                    else:
                        await func(event)
                else:
                    if plugin:
                        func(plugin, event)
                    else:
                        func(event)
            except Exception as e:
                LOG.error(f"执行过滤器函数失败: {func.__name__}, 错误: {e}")

    def _find_plugin_for_function(self, func: Callable) -> Optional["NcatBotPlugin"]:
        """借用插件实例缓存逻辑：从宿主插件查询函数所属实例。"""
        # 直接复用插件的映射缓存，如无则动态查找
        try:
            if hasattr(self.plugin, "func_plugin_map") and func in self.plugin.func_plugin_map:
                return self.plugin.func_plugin_map[func]
            # 动态查找
            plugins = self.plugin.list_plugins(obj=True)
            for plugin in plugins:
                plugin_class = plugin.__class__
                for name, value in plugin_class.__dict__.items():
                    if value is func:
                        self.plugin.func_plugin_map[func] = plugin  # 缓存
                        return plugin
            return None
        except Exception:
            return None


