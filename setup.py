"""
Python 包配置主文件 (基于 setuptools)

文件结构要求：
.
├── setup.py
├── pyproject.toml
├── requirements.txt
├── src/
│   └── PACKAGE_NAME/  # 你的包目录
│       ├── __init__.py
│       └── ...        # 其他代码文件
└── README.md          # 长描述内容来源
"""

import os
import re
from pathlib import Path
from setuptools import setup, find_packages

# 基础配置 --------------------------------------------------------------
PACKAGE_NAME = "ncatbot"  # 更改为你的包名 (PyPI显示的名称)
AUTHOR = "木子"         # 作者/维护者姓名
EMAIL = "lyh_02@qq.com"  # 联系邮箱
URL = "https://github.com/liyihao1110/ncatbot"  # 项目主页
DESCRIPTION = "NcatBot，基于 协议 的 QQ 机器人 Python SDK，快速开发，轻松部署。"  # 简短描述
LICENSE = "MIT 修改版"  # 许可证类型 (MIT/Apache 2.0/GPL等)

# 版本控制配置 -----------------------------------------------------------
def get_version():
    """动态获取包版本号 (从__init__.py读取)"""
    version_file = os.path.join("src", PACKAGE_NAME, "__init__.py")
    with open(version_file, encoding="utf-8") as f:
        version_match = re.search(
            r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", f.read(), re.M
        )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("无法找到版本信息！请检查 {}".format(version_file))

# 依赖管理 --------------------------------------------------------------
def parse_requirements(filename="requirements.txt"):
    """加载依赖项列表"""
    requirements = []
    with open(filename, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line)
    return requirements

# 长描述配置 (从README.md读取) --------------------------------------------
def get_long_description():
    """生成PyPI长描述"""
    readme_path = Path(__file__).parent / "README.md"
    with open(readme_path, encoding="utf-8") as f:
        return f.read()

# 主配置 ----------------------------------------------------------------
setup(
    # 基础元数据
    name=PACKAGE_NAME,
    version=get_version(),
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    description=DESCRIPTION,
    long_description=get_long_description(),
    long_description_content_type="text/markdown",  # 如果使用.md文件
    license=LICENSE,

    # 包结构配置
    package_dir={"": "src"},  # 指定包根目录
    packages=find_packages(
        where="src",  # 在src目录下查找
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]  # 排除测试代码
    ),
    include_package_data=True,  # 包含MANIFEST.in指定的数据文件

    # 依赖管理
    install_requires=parse_requirements(),  # 生产环境依赖
    extras_require={  # 可选依赖组
        "dev": [  # 开发依赖 (pip install .[dev])
            "pytest>=6.0",
            "black>=22.3",
            "mypy>=0.910",
        ],
        "docs": [  # 文档生成依赖
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ]
    },

    # 分类信息 (PyPI搜索优化)
    classifiers=[
        # 完整列表：https://pypi.org/classifiers/
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],

    # 入口点配置 (CLI工具)
    entry_points={
        "console_scripts": [  # 创建命令行工具
            "ncatbot=ncatbot.cli.main:main",  # 示例配置
        ],
    },

    # 高级配置
    python_requires=">=3.8",  # 最低Python版本要求
    zip_safe=False,  # 设为False以确保能正确解压包文件
    project_urls={  # 扩展项目链接 (PyPI右侧显示)
        "Documentation": "https://docs.ncatbot.xyz/",
        "Source Code": URL,
        "Bug Tracker": f"{URL}/issues",
    },
)