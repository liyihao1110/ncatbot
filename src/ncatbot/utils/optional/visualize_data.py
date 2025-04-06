# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-03-21 18:07:00
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-23 16:14:38
# @Description  : 权限树可视化
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
from ncatbot.utils.assets import Color


def visualize_tree(data, parent_prefix="", is_last=True, is_root=True, level=0):
    """将嵌套数据结构转换为美观的彩色树形图"""
    # 存储每一行的列表
    lines = []

    # 根据层级选择连接线的颜色,循环使用三种颜色
    connector_color = [
        Color.YELLOW,
        Color.MAGENTA,
        Color.CYAN,
    ][level % 3]

    # 定义树形图的连接线和填充字符
    # 垂直线,用于非最后一个子节点的后续行
    vertical_line = f"{connector_color}│{Color.RESET}   "
    # 水平线,用于连接中间节点
    horizontal_line = f"{connector_color}├──{Color.RESET} "
    # 角落线,用于连接最后一个节点
    corner_line = f"{connector_color}└──{Color.RESET} "
    # 空格填充,用于已结束分支的对齐
    space_fill = "    "

    # 如果数据是字典类型
    if isinstance(data, dict):
        # 获取字典的键值对
        items = tuple(data.items())
        for i, (key, value) in enumerate(items):
            # 判断是否是最后一个键值对
            is_last_item = i + 1 == len(items)

            # 生成当前行的前缀
            if is_root:  # 如果是根节点
                # 根据是否是最后一个子节点选择角落线或水平线
                prefix = corner_line if is_last_item else horizontal_line
                # 新的前缀用于子节点的递归调用
                new_prefix = space_fill if is_last_item else vertical_line
            else:  # 如果不是根节点
                # 根据父节点的前缀和是否是最后一个子节点生成前缀
                prefix = parent_prefix + (
                    corner_line if is_last_item else horizontal_line
                )
                new_prefix = parent_prefix + (
                    space_fill if is_last_item else vertical_line
                )

            # 处理键的显示,给键加上蓝色
            key_str = f"{Color.from_rgb(152, 245, 249)}{key}{Color.RESET}"
            # 将当前键添加到行列表
            lines.append(f"{prefix}{key_str}")

            # 递归处理子节点
            sub_lines = visualize_tree(
                value,  # 子节点的值
                parent_prefix=new_prefix,  # 新的父前缀
                is_last=is_last_item,  # 是否是最后一个子节点
                is_root=False,  # 不是根节点
                level=level + 1,  # 层级加1
            )
            # 将子节点的行添加到主行列表
            lines.extend(sub_lines)

    # 如果数据是列表类型
    elif isinstance(data, list):
        for i, item in enumerate(data):
            is_last_item = i + 1 == len(data)  # 判断是否是最后一个列表项
            bullet = f"{Color.WHITE}•{Color.RESET}"  # 列表项目符号

            # 生成当前行的前缀
            if is_last_item:  # 如果是最后一项
                prefix = parent_prefix + corner_line
                new_prefix = parent_prefix + space_fill
            else:  # 如果不是最后一项
                prefix = parent_prefix + horizontal_line
                new_prefix = parent_prefix + vertical_line

            # 将项目符号添加到行列表
            lines.append(f"{prefix}{bullet}")

            # 递归处理子节点
            sub_lines = visualize_tree(
                item,  # 子节点的值
                parent_prefix=new_prefix,  # 新的父前缀
                is_last=is_last_item,  # 是否是最后一个子节点
                is_root=False,  # 不是根节点
                level=level + 1,  # 层级加1
            )
            # 将子节点的行添加到主行列表
            lines.extend(sub_lines)

    # 如果是基本数据类型（非字典和列表）
    else:
        # 根据数据类型设置值的颜色
        value_color = Color.WHITE
        if isinstance(data, bool):  # 布尔值
            value_color = Color.GREEN if data else Color.RED
            data = str(data)  # 转换为字符串
        elif isinstance(data, (int, float)):  # 数值
            value_color = Color.CYAN
        elif data is None:  # None
            value_color = Color.GRAY
            data = "None"

        # 格式化值的字符串
        value_str = f"{value_color}{data}{Color.RESET}"
        # 根据是否是最后一个子节点选择连接线
        connector = corner_line if is_last else horizontal_line
        # 将值添加到行列表
        lines.append(f"{parent_prefix}{connector}{value_str}")

    # 返回所有行的列表
    return lines


# 示例用法
if __name__ == "__main__":
    sample_data = {
        "name": "Alice",
        "age": 30,
        "features": ["intelligent", "creative"],
        "children": [
            {"name": "Bob", "age": 5, "toys": ["train", "ball"]},
            {
                "name": "Charlie",
                "pet": None,
                "sex": 0,
            },
        ],
        "active": True,
    }

    # 生成树形图
    tree = visualize_tree(sample_data)
    # 打印树形图
    print("\n".join(tree))
