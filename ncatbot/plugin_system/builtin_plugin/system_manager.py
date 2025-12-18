from ..builtin_mixin import NcatBotPlugin
from .unified_registry import command_registry, filter_registry, root_filter
from .unified_registry.command_system.registry import option_group
from ..event.event import NcatBotEventFactory, NcatBotEvent
from ncatbot.core.event import BaseMessageEvent
import psutil
import ncatbot
from ncatbot.utils import get_log, PermissionGroup, run_coroutine, config
import threading
import time
import asyncio
import os
from pathlib import Path

LOG = get_log("SystemManager")


class SystemManager(NcatBotPlugin):
    version = "4.0.0"
    name = "SystemManager"
    author = "huan-yp"
    description = "ncatbot 系统管理插件"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._file_watcher_thread = None
        self._watch_stop_event = threading.Event()
        self._file_cache = {}  # 用于缓存文件的修改时间
        self._pending_plugin_dirs = set()  # 待处理的一级插件子目录
        self._last_process_time = 0  # 上次处理时间，用于去重

    def _file_change_callback(self, file_path: str) -> None:
        """文件变化的回调函数"""
        LOG.info(f"检测到文件变化: {file_path}")

        # 如果 debug 模式开启，处理插件目录并发送卸载/加载请求
        if getattr(config, "debug", False):
            plugins_dir = config.plugin.plugins_dir
            try:
                # 获取相对路径
                rel_path = os.path.relpath(file_path, plugins_dir)
                # 获取一级子目录
                parts = rel_path.split(os.sep)
                if len(parts) > 1:
                    first_level_dir = parts[0]
                    self._pending_plugin_dirs.add(first_level_dir)
                    LOG.debug(f"添加待处理插件目录: {first_level_dir}")
            except Exception as e:
                LOG.warning(f"处理文件路径时出错 {file_path}: {e}")

    def _watch_plugin_files(self) -> None:
        """守护线程：监视插件目录中的 .py 文件变化"""
        plugins_dir = config.plugin.plugins_dir

        if not os.path.exists(plugins_dir):
            LOG.warning(f"插件目录不存在: {plugins_dir}")
            return

        LOG.info(f"启动文件监视线程，监视目录: {plugins_dir}")

        while not self._watch_stop_event.is_set():
            try:
                # 遍历所有 .py 文件
                for py_file in Path(plugins_dir).rglob("*.py"):
                    file_path = str(py_file)

                    # 排除 site-packages 中的文件
                    if "site-packages" in file_path:
                        continue

                    try:
                        mod_time = os.path.getmtime(file_path)

                        # 如果文件不在缓存中，或修改时间改变了
                        if (
                            file_path not in self._file_cache
                            or self._file_cache[file_path] != mod_time
                        ):
                            self._file_cache[file_path] = mod_time
                            # 触发回调函数
                            self._file_change_callback(file_path)
                    except OSError as e:
                        LOG.warning(f"无法获取文件信息 {file_path}: {e}")

                # 检查是否有删除的文件（排除 site-packages）
                deleted_files = [
                    f
                    for f in self._file_cache.keys()
                    if not os.path.exists(f) or "site-packages" in f
                ]
                for deleted_file in deleted_files:
                    del self._file_cache[deleted_file]
                    if os.path.exists(deleted_file):
                        continue
                    LOG.info(f"检测到文件删除: {deleted_file}")
                    self._file_change_callback(deleted_file)

                # 处理待处理的插件目录
                current_time = time.time()
                if (
                    self._pending_plugin_dirs
                    and (current_time - self._last_process_time) >= 1
                ):
                    # 至少间隔 1 秒处理一次，避免频繁重复加载
                    # 100% 有线程安全问题，但是我不管了
                    asyncio.run(self._process_pending_plugin_dirs())
                    self._last_process_time = current_time

                # 每秒检查一次
                time.sleep(1)
            except Exception as e:
                LOG.error(f"文件监视线程出错: {e}")
                time.sleep(1)

    async def _process_pending_plugin_dirs(self) -> None:
        """处理待处理的插件目录：发送卸载和加载请求"""
        if not self._pending_plugin_dirs:
            return

        if not hasattr(self, "_first_process"):
            self._pending_plugin_dirs.clear()
            self._first_process = True
            return  # 跳过第一次处理，避免启动时误触发

        # 复制并清空待处理集合，避免重复处理
        dirs_to_process = self._pending_plugin_dirs.copy()
        self._pending_plugin_dirs.clear()

        LOG.info(f"处理修改的插件目录: {dirs_to_process}")

        for plugin_dir in dirs_to_process:
            try:
                # 发送卸载请求
                unload_event = NcatBotEventFactory.create_event(
                    "plugin_unload_request", name=plugin_dir
                )
                await self.event_bus.publish(unload_event)
                LOG.info(f"发送插件卸载请求: {plugin_dir}")

                # 稍微延迟后发送加载请求
                await run_coroutine(lambda: __import__("asyncio").sleep(0.5))

                # 发送加载请求
                load_event = NcatBotEventFactory.create_event(
                    "plugin_load_request", name=plugin_dir
                )
                await self.event_bus.publish(load_event)
                LOG.info(f"发送插件加载请求: {plugin_dir}")
            except Exception as e:
                LOG.error(f"处理插件目录 {plugin_dir} 时出错: {e}")

    async def on_load(self) -> None:
        self.register_handler("ncatbot.plugin_load_request", self.load_plugin)
        self.register_handler("ncatbot.plugin_unload_request", self.unload_plugin)

        # 启动文件监视守护线程
        self._watch_stop_event.clear()
        self._file_watcher_thread = threading.Thread(
            target=self._watch_plugin_files, daemon=True, name="PluginFileWatcher"
        )
        self._file_watcher_thread.start()
        LOG.info("文件监视守护线程已启动")

    @command_registry.command("ncatbot_status", aliases=["ncs"])
    @root_filter
    async def get_status(self, event: BaseMessageEvent) -> None:
        text = "ncatbot 状态:\n"
        text += f"插件数量: {len(self._loader.plugins)}\n"
        text += f"插件列表: {', '.join([plugin.name for plugin in self._loader.plugins.values()])}\n"
        text += f"CPU 使用率: {psutil.cpu_percent()}%\n"
        text += f"内存使用率: {psutil.virtual_memory().percent}%\n"
        text += f"NcatBot 版本: {ncatbot.__version__}\n"
        text += "Star NcatBot Meow~: https://github.com/liyihao1110/ncatbot\n"
        await event.reply(text)

    @command_registry.command("ncatbot_help", aliases=["nch"])
    @root_filter
    async def get_help(self, event: BaseMessageEvent) -> None:
        text = "ncatbot 帮助:\n"
        text += "/ncs 查看ncatbot状态\n"
        text += "/nch 查看ncatbot帮助\n"
        text += "开发中... 敬请期待\n"
        await event.reply(text)

    @command_registry.command("set_admin", aliases=["sa"])
    @option_group(
        choices=["add", "remove"], name="set", default="add", help="设置管理员"
    )
    @root_filter
    async def set_admin(
        self, event: BaseMessageEvent, user_id: str, set: str = "add"
    ) -> None:
        if user_id.startswith("At"):
            user_id = user_id.split("=")[1].split('"')[1]

        if set == "add":
            self.rbac_manager.assign_role_to_user(user_id, PermissionGroup.ADMIN.value)
            await event.reply(f"添加管理员 {user_id}", at=False)
        elif set == "remove":
            self.rbac_manager.unassign_role_to_user(
                user_id, PermissionGroup.ADMIN.value
            )
            await event.reply(f"删除管理员 {user_id}", at=False)

    @command_registry.command("set_config", aliases=["cfg"])
    @filter_registry.admin_filter
    async def set_config(
        self, event: BaseMessageEvent, plugin_name: str, config_name: str, value: str
    ) -> None:
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            await event.reply(f"未找到插件 {plugin_name}")
        configs = plugin.get_registered_configs()
        if config_name not in configs:
            await event.reply(f"插件 {plugin_name} 未注册配置 {config_name}")
        from ..builtin_mixin.config_mixin import Config

        config: Config = configs[config_name]
        oldvalue, newvalue = config.update(value)
        if config.on_change:
            run_coroutine(config.on_change, oldvalue, newvalue)
        await event.reply(f"插件 {plugin_name} 配置 {config_name} 更新为 {value}")

    async def unload_plugin(self, event: NcatBotEvent) -> bool:
        """卸载插件, 可以把自己卸了"""
        name = event.data.get("name")
        plugin = self.get_plugin(name)
        if not plugin:
            LOG.warning(f"尝试卸载不存在的插件 {name}")
            return False
        await self._loader.unload_plugin(name)
        await self.event_bus.publish(
            NcatBotEventFactory.create_event("plugin_unload", name=name)
        )
        return True

    async def load_plugin(self, event: NcatBotEvent):
        """加载插件"""
        name = event.data.get("name")
        plugin = await self._loader.load_plugin(name)
        if self._loader.get_plugin(name) is None:
            LOG.warning(f"尝试加载失败的插件 {name}")
            return False
        await self.event_bus.publish(
            NcatBotEventFactory.create_event("plugin_load", name=plugin.name)
        )
        return True

    async def on_unload(self) -> None:
        """插件卸载时的清理工作"""
        # 停止文件监视线程
        if self._file_watcher_thread and self._file_watcher_thread.is_alive():
            self._watch_stop_event.set()
            self._file_watcher_thread.join(timeout=5)
            LOG.info("文件监视守护线程已停止")
