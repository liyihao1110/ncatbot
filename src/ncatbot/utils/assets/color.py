# 终端颜色配置


class Color:
    """
    用于在终端中显示颜色和样式。

    包含以下功能:
    - 前景: 设置颜色
    - 背景: 设置背景颜色
    - 样式: 设置样式（如加粗、下划线、反转）
    - RESET: 重置所有颜色和样式
    - from_rgb: 从 RGB 代码创建颜色
    """

    _COLOR = True  # 假设终端支持 ANSI 颜色,实际使用时可能需要检测

    def __getattribute__(self, name):
        if self._COLOR:
            return super().__getattribute__(name)
        else:
            return ""

    # 前景颜色
    BLACK = "\033[30m"
    """前景-黑"""
    RED = "\033[31m"
    """前景-红"""
    GREEN = "\033[32m"
    """前景-绿"""
    YELLOW = "\033[33m"
    """前景-黄"""
    BLUE = "\033[34m"
    """前景-蓝"""
    MAGENTA = "\033[35m"
    """前景-品红"""
    CYAN = "\033[36m"
    """前景-青"""
    WHITE = "\033[37m"
    """前景-白"""
    GRAY = "\033[90m"
    """前景-灰"""

    # 背景颜色
    BG_BLACK = "\033[40m"
    """背景-黑"""
    BG_RED = "\033[41m"
    """背景-红"""
    BG_GREEN = "\033[42m"
    """背景-绿"""
    BG_YELLOW = "\033[43m"
    """背景-黄"""
    BG_BLUE = "\033[44m"
    """背景-蓝"""
    BG_MAGENTA = "\033[45m"
    """背景-品红"""
    BG_CYAN = "\033[46m"
    """背景-青"""
    BG_WHITE = "\033[47m"
    """背景-白"""
    BG_GRAY = "\033[100m"
    """背景-灰"""

    # 样式
    RESET = "\033[0m"
    """重置所有颜色和样式"""
    BOLD = "\033[1m"
    """加粗"""
    UNDERLINE = "\033[4m"
    """下划线"""
    REVERSE = "\033[7m"
    """反转（前景色和背景色互换）"""
    ITALIC = "\033[3m"
    """斜体"""
    BLINK = "\033[5m"
    """闪烁"""
    STRIKE = "\033[9m"
    """删除线"""

    @classmethod
    def from_rgb(cls, r, g, b, background=False):
        """
        从 RGB 颜色代码创建颜色代码。

        :param r: 红色分量 (0-255)
        :param g: 绿色分量 (0-255)
        :param b: 蓝色分量 (0-255)
        :param background: 是否是背景颜色,默认为前景颜色
        :return: ANSI 颜色代码
        """
        if not cls._COLOR:
            return ""
        if background:
            return f"\033[48;2;{r};{g};{b}m"
        else:
            return f"\033[38;2;{r};{g};{b}m"

    @classmethod
    def rgb(cls, r, g, b):
        """
        创建前景 RGB 颜色。

        :param r: 红色分量 (0-255)
        :param g: 绿色分量 (0-255)
        :param b: 蓝色分量 (0-255)
        :return: ANSI 前景颜色代码
        """
        return cls.from_rgb(r, g, b, background=False)

    @classmethod
    def bg_rgb(cls, r, g, b):
        """
        创建背景 RGB 颜色。

        :param r: 红色分量 (0-255)
        :param g: 绿色分量 (0-255)
        :param b: 蓝色分量 (0-255)
        :return: ANSI 背景颜色代码
        """
        return cls.from_rgb(r, g, b, background=True)

    # 256 色模式
    @classmethod
    def color256(cls, color_code, background=False):
        """
        使用 256 色模式创建颜色。

        :param color_code: 256 色中的颜色编号 (0-255)
        :param background: 是否是背景颜色,默认为前景颜色
        :return: ANSI 颜色代码
        """
        if not cls._COLOR:
            return ""
        if background:
            return f"\033[48;5;{color_code}m"
        else:
            return f"\033[38;5;{color_code}m"

    @classmethod
    def rgb256(cls, r, g, b, background=False):
        """
        将 RGB 颜色转换为最接近的 256 色。

        :param r: 红色分量 (0-255)
        :param g: 绿色分量 (0-255)
        :param b: 蓝色分量 (0-255)
        :param background: 是否是背景颜色,默认为前景颜色
        :return: ANSI 256 色代码
        """
        if not cls._COLOR:
            return ""

        # 将 RGB 转换为 256 色
        def rgb_to_256(r, g, b):
            if r == g == b:  # 灰度
                if r < 8:
                    return 16
                if r > 248:
                    return 231
                return round((r - 8) / 247 * 24) + 232
            return (
                16
                + (36 * round(r / 255 * 5))
                + (6 * round(g / 255 * 5))
                + round(b / 255 * 5)
            )

        color_code = rgb_to_256(r, g, b)
        return cls.color256(color_code, background)
