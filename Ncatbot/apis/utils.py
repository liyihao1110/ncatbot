import os
import imgkit
import mistune
import zipfile
import sys

from PIL import Image, ImageDraw

path = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')

def markdown_to_image_beautified(md_text, output_path=path+'/output.png', wkhtmltoimage_path=path+'/wkhtmltoimage.exe'):
    """
    将Markdown文本转换为美化后的图片文件，并对图片进行圆角处理。
    下载wkhtmltoimage.exe的地址：https://wkhtmltopdf.org/downloads.html

    :param md_text: Markdown格式的字符串
    :param output_path: 输出图片的文件路径，默认为'output.png'
    :param wkhtmltoimage_path: wkhtmltoimage可执行文件的路径，如果在系统环境变量中已配置则无需提供
    :return: 生成的图片文件路径
    """
    # 定义HTML样式
    style = """
    <style>
        body {
            font-family: "华文细黑", "Microsoft YaHei";
            color: #333;
            padding: 5px;
            border-radius: 3px;
            background-color: #f9f9f9;
            margin: 0;
            line-height: 1.6;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            font-weight: bold;
        }
        code, pre {
            background-color: #ecf0f1;
            padding: 5px;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
        }
        a {
            color: #2980b9;
            font-weight: bold;
        }
        p {
            margin-bottom: 15px;
        }

        .container {
            margin: auto;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            background-color: white;
            padding: 20px;
            border-radius: 8px;
        }
    </style>
    """

    if 'win' in sys.platform:
        if not os.path.exists(wkhtmltoimage_path):
            print("wkhtmltoimage.exe未找到，启动初始化，第一次初始化可能比较慢，并且导致发送失败，请稍后重试")
            with zipfile.ZipFile(path+'/wkhtmltoimage.zip', 'r') as zip_ref:
                zip_ref.extractall(path)
        else:
            pass
    elif 'linux' in sys.platform:
        print("灰度...无法使用")
        # TODO: 等待linux大佬添加支持
        pass
    else:
        print("不支持的操作系统")

    # 使用mistune将Markdown文本转换为HTML
    markdown = mistune.Markdown(renderer=mistune.HTMLRenderer())
    html_content = markdown(md_text)

    # 包装HTML内容以便应用样式
    full_html = f"<!DOCTYPE html><html><head>{style}</head><body><div class='container'>{html_content}</div></body></html>"
    config = imgkit.config(wkhtmltoimage=wkhtmltoimage_path) if wkhtmltoimage_path else None

    # 使用imgkit将HTML内容转换为临时图片
    temp_output_path = 'temp_output.png'
    imgkit.from_string(full_html, temp_output_path, config=config)

    # 加载临时图片并进行圆角处理
    image = Image.open(temp_output_path).convert("RGBA")
    width, height = image.size

    # 创建一个带有圆角的掩码
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    radius = 20  # 圆角半径
    draw.rounded_rectangle((0, 0, width, height), radius, fill=255)

    # 应用掩码并保存最终图片
    result = Image.new("RGBA", (width, height))
    result.paste(image, mask=mask)
    result.save(output_path)

    # 删除临时图片
    os.remove(temp_output_path)
    return output_path