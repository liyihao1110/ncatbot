import os
import re
from pathlib import Path
from setuptools import setup, find_packages

# 基础配置
PACKAGE_NAME = "ncatbot"
AUTHOR = "木子"
EMAIL = "lyh_02@qq.com"
URL = "https://github.com/liyihao1110/ncatbot"
DESCRIPTION = "NcatBot，基于协议的QQ机器人Python SDK"
LICENSE = "MIT"

def get_version():
    """从__init__.py获取版本号"""
    init_file = Path(__file__).parent / "ncatbot" / "__init__.py"
    with open(init_file, encoding="utf-8") as f:
        version_match = re.search(
            r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", 
            f.read(), 
            re.M
        )
    if version_match:
        return version_match.group(1)
    raise RuntimeError(f"无法在 {init_file} 中找到版本信息")

def get_requirements():
    """获取依赖列表"""
    req_file = Path(__file__).parent / "requirements.txt"
    with open(req_file, encoding="utf-8") as f:
        return [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith("#")
        ]

def get_long_description():
    """获取长描述"""
    readme = Path(__file__).parent / "README.md"
    return readme.read_text(encoding="utf-8")

# 主配置
setup(
    # 基础元数据
    name=PACKAGE_NAME,
    version=get_version(),
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    description=DESCRIPTION,
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    license=LICENSE,
    
    # 包配置
    packages=find_packages(
        include=["ncatbot", "ncatbot.*"],
        exclude=["tests*", "docs*", "examples*"]
    ),
    package_dir={"": "."},  # 从根目录查找包
    include_package_data=True,
    zip_safe=False,

    # 依赖管理
    install_requires=get_requirements(),
    python_requires=">=3.8",
    
    # 入口点配置（确保路径正确）
    entry_points={
        "console_scripts": [
            "ncatbot=ncatbot.cli.main:main",
        ],
    },
    
    # 分类信息
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # 项目URLs
    project_urls={
        "Source": URL,
        "Bug Reports": f"{URL}/issues",
        "Documentation": f"{URL}/wiki",
    },
)