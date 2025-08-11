from .func_mixin import FunctionMixin, Filter, Func
from typing import Callable, Any, List
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils import PermissionGroup
import asyncio
import functools

class AliasFilter(Filter):
    def __init__(self, name: str, aliases: List[str]):
        self.name = name
        self.aliases = aliases
    
    def check(self, event: BaseMessageEvent) -> bool:
        if event.raw_message.startswith("/" + self.name):
            return True
        if self.aliases is not None:
            for alias in self.aliases:
                if event.raw_message.startswith("/" + alias):
                    return True
        return False
    
class Command:
    def __init__(self, data: dict):
        self.name = data['name']
        self.aliases = data['aliases']
        self.permission = data['permission']
        self.description = data['description']
        self.usage = data['usage']
        self.examples = data['examples']
        self.func: Func = data['func']
    
    def __str__(self) -> str:
        return f"{self.name} - {self.description}"
    
    def __repr__(self) -> str:
        return f"Command(name={self.name}, permission={self.permission}, description={self.description}, usage={self.usage}, examples={self.examples}, func={self.func})"
        
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Command):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False

class CommandMixin(FunctionMixin):
    _registered_command_activators: List[str] = []
    def unregister_command(self, name: str):
        for command in self._registered_commands:
            if command.name == name:
                self.unregister_func(command.func.name)
                self._registered_commands.remove(command)
                break
        else:
            raise ValueError(f"命令 {name} 不存在")
        
    def get_registered_commands(self) -> List[Command]:
        if not hasattr(self, '_registered_commands'):
            self._registered_commands = []
        return self._registered_commands
    
    def _create_command_handler(self, handler: Callable) -> Callable:
        @functools.wraps(handler)
        async def warpped_handler(event: BaseMessageEvent, handler=handler):
            args = event.raw_message.split()
            if asyncio.iscoroutinefunction(handler):
                return await handler(event, args)
            else:
                return handler(event, args)
        return warpped_handler
    
    def register_command(self, name: str, handler: Callable[[BaseMessageEvent, list[str]], Any], aliases: List[str] = None, description: str = "", usage: str = "", examples: List[str] = None, permission: PermissionGroup = PermissionGroup.USER.value, timeout: float = None) -> Command:
        # TODO 提示已经注册的别名
        # TODO 限定参数
        if not hasattr(self, '_registered_commands'):
            self._registered_commands: List[Command] = []
        if name in self._registered_commands:
            raise ValueError(f"命令 {name} 已经存在")
        
        warpped_handler = self._create_command_handler(handler)
        func = self._register_func(name, warpped_handler, AliasFilter(name, aliases).check, description=description, usage=usage, examples=examples, permission=PermissionGroup.USER.value, timeout=timeout)
        command = Command({
            'name': name,
            'aliases': aliases,
            'permission': permission,
            'description': description,
            'usage': usage,
            'examples': examples,
            'func': func
        })
        self._registered_commands.append(command)
        return command
    
    def register_user_command(self, name: str, handler: Callable[[BaseMessageEvent, list[str]], Any], aliases: List[str] = None, description: str = "", usage: str = "", examples: List[str] = None, timeout: float = None) -> Command:
        return self.register_command(name, handler, aliases, description, usage, examples, PermissionGroup.USER.value, timeout)
        
    def register_admin_command(self, name: str, handler: Callable[[list[str], BaseMessageEvent], Any], aliases: List[str] = None, description: str = "", usage: str = "", examples: List[str] = None, timeout: float = None) -> Command:
        return self.register_command(name, handler, aliases, description, usage, examples, PermissionGroup.ADMIN.value, timeout)