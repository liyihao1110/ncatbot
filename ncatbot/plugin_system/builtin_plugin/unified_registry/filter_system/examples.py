"""过滤器系统 v2.0 使用示例

这个文件展示了如何使用新的过滤器系统。
"""

from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import (
    filter_registry,
    BaseFilter,
    GroupFilter,
    PrivateFilter,
    AdminFilter,
    RootFilter,
    CustomFilter,
    filter,
    group_only,
    private_only,
    admin_only,
    root_only,
    admin_group_only,
    admin_private_only,
)

# 示例1: 注册过滤器实例
def example_1():
    """示例1: 注册过滤器实例"""
    # 注册内置过滤器
    filter_registry.register_filter("group_only", GroupFilter())
    filter_registry.register_filter("private_only", PrivateFilter())
    filter_registry.register_filter("admin_only", AdminFilter())
    filter_registry.register_filter("root_only", RootFilter())

# 示例2: 注册自定义过滤器函数
def example_2():
    """示例2: 注册自定义过滤器函数"""
    
    @filter_registry.register("time_check")
    def time_filter(event):
        """时间检查过滤器 - 只在白天工作"""
        import datetime
        current_hour = datetime.datetime.now().hour
        return 6 <= current_hour <= 22
    
    @filter_registry.register("weekend_only")
    def weekend_filter(event):
        """周末专用过滤器"""
        import datetime
        return datetime.datetime.now().weekday() >= 5

# 示例3: 使用装饰器为函数添加过滤器
def example_3():
    """示例3: 使用装饰器为函数添加过滤器"""
    
    # 使用内置装饰器
    @group_only
    def handle_group_message(event):
        """只处理群聊消息"""
        return f"群聊消息: {event.text}"
    
    @private_only
    def handle_private_message(event):
        """只处理私聊消息"""
        return f"私聊消息: {event.text}"
    
    @admin_only
    def admin_command(event):
        """管理员专用命令"""
        return "管理员命令执行成功"
    
    @admin_group_only
    def admin_group_command(event):
        """管理员群聊专用命令"""
        return "管理员群聊命令执行成功"

# 示例4: 使用 filter 装饰器组合多个过滤器
def example_4():
    """示例4: 使用 filter 装饰器组合多个过滤器"""
    
    @filter(GroupFilter(), AdminFilter())
    def complex_admin_group_command(event):
        """复合过滤器: 群聊 + 管理员"""
        return "复合过滤器命令执行成功"
    
    @filter("time_check", "weekend_only")
    def weekend_daytime_command(event):
        """使用已注册的过滤器名称"""
        return "周末白天命令执行成功"
    
    @filter(GroupFilter(), "time_check")
    def mixed_filter_command(event):
        """混合使用过滤器实例和名称"""
        return "混合过滤器命令执行成功"

# 示例5: 自定义过滤器类
def example_5():
    """示例5: 自定义过滤器类"""
    
    class VIPFilter(BaseFilter):
        """VIP用户过滤器"""
        
        def __init__(self, vip_list=None):
            super().__init__("vip_filter")
            self.vip_list = vip_list or []
        
        def check(self, event):
            """检查是否为VIP用户"""
            return event.user_id in self.vip_list
    
    # 注册自定义过滤器
    vip_filter = VIPFilter([123456, 789012])
    filter_registry.register_filter("vip_only", vip_filter)
    
    @filter("vip_only")
    def vip_command(event):
        """VIP专用命令"""
        return "VIP命令执行成功"

# 示例6: 查询和管理过滤器
def example_6():
    """示例6: 查询和管理过滤器"""
    
    # 查询已注册的过滤器
    all_filters = filter_registry.list_filters()
    print(f"已注册的过滤器: {[f.name for f in all_filters]}")
    
    # 获取特定过滤器
    group_filter = filter_registry.get_filter_instance("group_only")
    if group_filter:
        print(f"找到过滤器: {group_filter}")
    
    # 移除过滤器
    filter_registry.remove_filter("old_filter")
    
    # 清理所有过滤器
    # filter_registry.clear_all()

if __name__ == "__main__":
    # 运行示例
    example_1()
    example_2() 
    example_3()
    example_4()
    example_5()
    example_6()
    
    print("过滤器系统 v2.0 示例运行完成!")