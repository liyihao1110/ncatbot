# 发送图片 MarkDown 文件

import os
import platform
import tempfile
from pathlib import Path

import markdown
from pygments.formatters import HtmlFormatter
from pyppeteer import launch

from ncatbot.utils.logger import get_log

_log = get_log("utils")


def read_file(file_path) -> any:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def get_chrome_path():
    """
    获取 Chrome 浏览器的可执行文件路径。
    在 Windows 上通过注册表查找，在 Linux 上通过 which 命令查找。
    """
    system = platform.system()

    if system == "Windows":
        import winreg

        registry_keys = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
        ]
        for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            for sub_key in registry_keys:
                try:
                    with winreg.OpenKey(root, sub_key) as key:
                        path, _ = winreg.QueryValueEx(key, "")
                        if os.path.exists(path):
                            return path
                except FileNotFoundError:
                    continue
    elif system == "Linux":
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/snap/bin/chromium",
            "/snap/bin/chromium-browser",
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                return path
        # 使用 which 命令查找
        which_chrome = os.popen("which google-chrome").read().strip()
        if which_chrome and os.path.exists(which_chrome):
            return which_chrome
        which_chromium = os.popen("which chromium").read().strip()
        if which_chromium and os.path.exists(which_chromium):
            return which_chromium
    if system == "Darwin":  # macOS 系统
        chrome_paths = [
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
        ]
        for path in chrome_paths:
            if path.exists():
                return str(path)

        # 如果没有找到，则检查 pyppeteer 下载的 Chromium
        local_chromium_path = (
            Path.home() / "Library/Application Support/pyppeteer/local-chromium"
        )
        if local_chromium_path.exists():
            chrome_folders = list(local_chromium_path.iterdir())
            if chrome_folders:  # 确保有文件夹
                chrome_folder = chrome_folders[0]  # 取第一个文件夹
                chrome_executable = (
                    chrome_folder
                    / "chrome-mac"
                    / "Chromium.app"
                    / "Contents"
                    / "MacOS"
                    / "Chromium"
                )
                if chrome_executable.exists():
                    return str(chrome_executable)

    return None


def markdown_to_html(md_content, external_css_urls=None, custom_css=""):
    """
    将 Markdown 文本转换为 HTML，并导入外部 CSS 模板及自定义 CSS 样式。

    :param md_content: Markdown 文本内容
    :param external_css_urls: 外部 CSS 链接列表
    :param custom_css: 自定义 CSS 样式，将嵌入在 <style> 标签中
    :return: 完整 HTML 字符串
    """
    html_body = markdown.markdown(md_content, extensions=["extra", "codehilite"])
    css_links = ""
    if external_css_urls:
        for url in external_css_urls:
            css_links += f'<link rel="stylesheet" href="{url}">\n'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Markdown 转 HTML</title>
    {css_links}
    <style>
    {custom_css}
    </style>
</head>
<body>
<div class="container">
{html_body}
</div>
</body>
</html>
"""
    return html


async def html_to_png(html_content, output_png, chrome_executable=None):
    """
    利用 pyppeteer 启动 Chrome，将 HTML 渲染后保存为 PNG 图片。

    :param html_content: HTML 内容字符串
    :param output_png: 输出 PNG 文件的路径
    :param chrome_executable: Chrome 浏览器的可执行文件路径（可选）
    """
    with tempfile.NamedTemporaryFile(
        "w", delete=False, suffix=".html", encoding="utf-8"
    ) as f:
        html_file = f.name
        f.write(html_content)

    file_url = "file:///" + html_file.replace("\\", "/")

    # 启动浏览器，若未指定 chrome_executable，则使用 pyppeteer 默认的 Chromium
    launch_options = {"headless": True, "args": ["--no-sandbox"]}
    if chrome_executable:
        launch_options["executablePath"] = chrome_executable

    browser = await launch(launch_options)
    page = await browser.newPage()

    await page.goto(file_url, {"waitUntil": "networkidle0"})

    content_height = await page.evaluate("document.documentElement.scrollHeight")
    await page.setViewport(
        {"width": 1280, "height": content_height}
    )  # 如果觉得截取出来的图片过宽，修改width即可

    await page.screenshot({"path": output_png, "fullPage": False})

    await browser.close()

    os.remove(html_file)


async def md_maker(md_content):
    """
    将 Markdown 文本转换为 HTML，并生成 PNG 图片。
    :param md_content: Markdown 文本内容
    :return: 生成的 PNG 图片路径
    """
    current_path = os.path.dirname(os.path.abspath(__file__))
    external_css = read_file(os.path.join(current_path, "template/external.css"))
    highlight_css = HtmlFormatter().get_style_defs(".codehilite")
    custom_css = f"""
/* 基本重置与布局 */
html, body {{
    margin: 0;
    padding: 0;
    background-color: #f8f9fa;
    font-family: 'Helvetica Neue', Arial, sans-serif;  /* 现代化字体 */
}}
body {{
    padding: 20px;
}}

/* container 控制宽度 */
.container {{
    max-width: 960px;
    margin: auto;
}}

/* 自动换行处理，防止代码块超出页面宽度 */
pre code {{
    white-space: pre-wrap;
    word-break: break-all;
    font-family: 'Fira Code', 'Courier New', monospace;  /* 代码字体 */
}}

/* Pygments 代码高亮样式 */
{highlight_css}

/* 补充代码块背景和内边距（保证背景模板显示） */
.codehilite {{
    background: #f0f0f0;  /* 浅灰色背景 */
    color: #000000;
    padding: 1em;
    border-radius: 5px;
    overflow-x: auto;
    font-family: 'Fira Code', 'Courier New', monospace;  /* 代码字体 */
}}
pre.codehilite {{
    background: #f0f0f0;  /* 浅灰色背景 */
    color: #000000;
    padding: 1em;
    border-radius: 5px;
    overflow-x: auto;
    font-family: 'Fira Code', 'Courier New', monospace;  /* 代码字体 */
}}
/* 表格样式 */
table, th, td {{
    border: 1px solid #dee2e6;
    border-collapse: collapse;
}}
th, td {{
    padding: 0.75em;
    text-align: left;
}}
/* 针对超长文本、表格等设置 */
table {{
    width: 100%;
    margin-bottom: 1em;
}}
"""
    html_content = markdown_to_html(
        md_content, external_css_urls=external_css, custom_css=custom_css
    )
    chrome_path = get_chrome_path()
    if chrome_path is None:
        _log.info("未在注册表中找到 Chrome 浏览器路径，尝试自动安装Chromium")
        # raise Exception("未找到 Chrome 浏览器路径")
    else:
        _log.debug(f"Chrome 路径：{chrome_path}")
    output_png = os.path.join(tempfile.gettempdir(), "markdown.png")
    await html_to_png(html_content, output_png, chrome_path)
    return output_png
