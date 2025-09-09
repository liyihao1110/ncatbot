"""现代化命令注册系统使用示例

展示各种命令定义方式和高级特性。
"""

from typing import Union
from ncatbot.core.event.message_segment.message_segment import MessageSegment
from . import registry


# ============= 基础命令示例 =============

@registry.command("hello", description="简单的问候命令")
def hello_command(event):
    """返回问候信息"""
    return "Hello, World! 👋"


@registry.command("echo", description="回显输入内容")
def echo_command(event, message: str):
    """回显用户输入的消息
    
    Args:
        message: 要回显的消息
    """
    return f"你说: {message}"


# ============= 带默认值的命令 =============

@registry.command("greet", description="个性化问候")
def greet_command(event, name: str, times: int = 1):
    """问候指定用户指定次数
    
    Args:
        name: 用户名
        times: 问候次数（默认1次）
    """
    return f"Hello {name}! " * times


# ============= 带选项的命令 =============

@registry.command("backup", description="备份文件")
@registry.option("-v", "--verbose", help="显示详细信息")
@registry.option("-f", "--force", help="强制备份")
@registry.option("--dry-run", help="试运行模式")
def backup_command(event, path: str, verbose=False, force=False, dry_run=False):
    """备份指定路径的文件
    
    Args:
        path: 要备份的路径
    """
    result = []
    
    if dry_run:
        result.append("🔍 试运行模式")
    
    result.append(f"📁 备份路径: {path}")
    
    if force:
        result.append("⚡ 强制模式")
    
    if verbose:
        result.append("📋 详细信息: 开始备份...")
        result.append("📋 检查文件完整性...")
        result.append("📋 创建备份索引...")
    
    result.append("✅ 备份完成!")
    return "\n".join(result)


# ============= 带命名参数的命令 =============

@registry.command("deploy", description="部署应用")
@registry.param("env", type=str, default="dev", choices=["dev", "test", "prod"], 
                help="部署环境")
@registry.param("port", type=int, default=8080, help="服务端口")
@registry.param("workers", type=int, default=1, help="工作进程数")
@registry.option("-d", "--dry-run", help="试运行")
@registry.option("-q", "--quiet", help="静默模式")
def deploy_command(event, app_name: str, env="dev", port=8080, workers=1, 
                  dry_run=False, quiet=False):
    """部署应用到指定环境
    
    Args:
        app_name: 应用名称
    """
    if not quiet:
        result = [f"🚀 部署应用: {app_name}"]
        result.append(f"🌍 环境: {env}")
        result.append(f"🔌 端口: {port}")
        result.append(f"👥 工作进程: {workers}")
        
        if dry_run:
            result.append("🔍 试运行模式 - 不会实际部署")
        else:
            result.append("✅ 部署成功!")
        
        return "\n".join(result)
    else:
        return "部署完成" if not dry_run else "试运行完成"


# ============= 多类型参数示例 =============


@registry.command("process", description="处理文件或数据")
@registry.param("input", type=[str, MessageSegment],
                help="输入数据",
                type_hints={
                    str: "文件路径或文本内容",
                    MessageSegment: "图片或文件"
                },
                type_examples={
                    str: ["/path/to/file.txt", "文本内容"],
                    MessageSegment: ["[图片]", "[文件]"]
                })
@registry.option("--format", type=str, choices=["json", "xml", "text"], 
                default="text", help="输出格式")
def process_command(event, input_data, format="text"):
    """处理输入的文件或数据
    
    Args:
        input_data: 输入数据
    """
    if isinstance(input_data, str):
        result = f"📄 处理文本数据: {input_data}"
    else:
        result = f"🖼️ 处理媒体文件: {input_data.type}"
    
    result += f"\n📋 输出格式: {format}"
    return result


# ============= 互斥选项组示例 =============

@registry.command("format", description="格式化数据")
@registry.option_group(1, name="输出格式", mutually_exclusive=True, required=True)
@registry.option("-j", "--json", group=1, help="JSON格式输出")
@registry.option("-x", "--xml", group=1, help="XML格式输出") 
@registry.option("-y", "--yaml", group=1, help="YAML格式输出")
@registry.option("-t", "--text", group=1, help="纯文本输出")
def format_command(event, data: str, json=False, xml=False, yaml=False, text=False):
    """将数据格式化为指定格式
    
    Args:
        data: 要格式化的数据
    """
    if json:
        return f"📋 JSON格式:\n{{\n  \"data\": \"{data}\"\n}}"
    elif xml:
        return f"📋 XML格式:\n<data>{data}</data>"
    elif yaml:
        return f"📋 YAML格式:\ndata: {data}"
    elif text:
        return f"📋 文本格式:\n{data}"
    else:
        return "❌ 请选择一种输出格式"


# ============= 权限控制示例已移除 =============


# ============= 命令组示例 =============

# 创建管理员命令组
admin_group = registry.group("admin", description="管理员专用命令")

@admin_group.command("user", description="用户管理")
@registry.option("-l", "--list", help="列出所有用户")
@registry.option("-a", "--add", help="添加用户")
@registry.option("-d", "--delete", help="删除用户")
@registry.param("username", type=str, default="", help="用户名")
def admin_user_command(event, username="", list_users=False, add=False, delete=False):
    """管理用户账户"""
    if list_users:
        return "👥 用户列表:\n- Alice\n- Bob\n- Charlie"
    elif add and username:
        return f"✅ 添加用户: {username}"
    elif delete and username:
        return f"❌ 删除用户: {username}"
    else:
        return "❓ 请指定操作: --list, --add, --delete"


@admin_group.command("system", description="系统管理")
@registry.option("--status", help="查看系统状态")
@registry.option("--restart", help="重启系统")
@registry.option("--backup", help="备份系统")
def admin_system_command(event, status=False, restart=False, backup=False):
    """管理系统"""
    if status:
        return "📊 系统状态: 正常运行\n💾 内存使用: 45%\n💿 磁盘使用: 67%"
    elif restart:
        return "🔄 系统重启中..."
    elif backup:
        return "💾 系统备份中..."
    else:
        return "❓ 请指定操作: --status, --restart, --backup"


# 创建数据库子组
db_group = admin_group.group("db", description="数据库管理")

@db_group.command("backup", description="数据库备份")
@registry.param("target", type=str, help="备份目标路径")
@registry.option("--compress", help="压缩备份文件")
def db_backup_command(event, target: str, compress=False):
    """备份数据库"""
    result = f"🗄️ 备份数据库到: {target}"
    if compress:
        result += "\n📦 启用压缩"
    result += "\n✅ 备份完成"
    return result


@db_group.command("restore", description="数据库恢复")
@registry.param("source", type=str, help="备份文件路径")
@registry.option("--force", help="强制恢复")
def db_restore_command(event, source: str, force=False):
    """恢复数据库"""
    if force:
        return f"💥 强制恢复数据库从: {source}\n⚠️ 所有现有数据将被覆盖!\n✅ 恢复完成"
    else:
        return f"🔄 恢复数据库从: {source}\n✅ 恢复完成"


# ============= 复杂参数验证示例 =============

@registry.command("calculate", description="计算器")
@registry.param("precision", type=int, default=2, 
                help="小数精度",
                validator=lambda x: 0 <= x <= 10,
                examples=["2", "5", "10"])
@registry.option("-r", "--round", help="四舍五入结果")
@registry.option("--scientific", help="科学计数法显示")
def calculate_command(event, expression: str, precision=2, round_result=False, scientific=False):
    """计算数学表达式
    
    Args:
        expression: 数学表达式
    """
    try:
        # 这里应该有实际的计算逻辑，为了示例简化
        result = eval(expression)  # 注意：实际应用中不要使用eval
        
        if round_result:
            result = round(result, precision)
        else:
            result = round(result, precision)
        
        if scientific:
            return f"🔢 结果: {result:.{precision}e}"
        else:
            return f"🔢 结果: {result}"
    except Exception as e:
        return f"❌ 计算错误: {str(e)}"


# ============= 帮助命令示例 =============

@registry.command("help", description="显示帮助信息")
def help_command(event, command_name: str = ""):
    """显示命令帮助信息
    
    Args:
        command_name: 要查看帮助的命令名（可选）
    """
    from .help_system import HelpGenerator
    
    help_gen = HelpGenerator()
    
    if command_name:
        # 查找特定命令
        cmd_def = registry.find_command(f"/{command_name}")
        if cmd_def:
            return help_gen.generate_command_help(cmd_def)
        else:
            available_commands = registry.get_command_names()
            return f"❌ 未找到命令 '{command_name}'\n💡 可用命令: {', '.join(available_commands[:10])}"
    else:
        # 显示所有命令
        all_commands = registry.get_all_commands()
        return help_gen.generate_command_list(all_commands)


# ============= 使用示例函数 =============

def demo_commands():
    """演示各种命令的使用"""
    
    print("🎯 现代化命令注册系统演示")
    print("=" * 50)
    
    # 模拟命令输入
    test_commands = [
        "/hello",
        "/greet Alice 3",
        "/backup /home/user --verbose --force",
        "/deploy myapp --env=prod --port=3000 --dry-run",
        "/mention Alice 你好吗？",
        "/format 'some data' --json",
        "/admin user --list",
        "/admin db backup /backup --compress",
        "/calculate '2+3*4' --precision=1 --round",
        "/help",
        "/help deploy"
    ]
    
    for cmd_text in test_commands:
        print(f"\n💬 命令: {cmd_text}")
        
        # 查找命令
        cmd_def = registry.find_command(cmd_text)
        if cmd_def:
            print(f"✅ 找到命令: {cmd_def.name}")
            print(f"📝 描述: {cmd_def.description}")
            
            # 这里实际应用中会解析参数并执行命令
            # 为了演示，只显示命令信息
        else:
            print("❌ 命令未找到")
        
        print("-" * 30)


if __name__ == "__main__":
    demo_commands()
