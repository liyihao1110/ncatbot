import os

from setuptools import __version__, find_packages, setup

init_path = os.path.join(os.path.dirname(__file__), "ncatbot/__init__.py")

with open(init_path, "r") as f:
    exec(f.read())

version = __version__


setup(
    name="ncatbot",
    version=version,
    author="木子",
    author_email="yihaoli_2002@foxmail.com",
    description="NapCat Python SDK, 提供一站式开发部署方案",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/liyihao1110/ncatbot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.9",
    install_requires=[
        "websockets~=10.4",
        "httpx~=0.28.1",
        "psutil~=6.1.1",
        "tqdm~=4.67.1",
        "requests~=2.32.3",
        "Markdown~=3.7",
        "Pygments~=2.19.1",
        "pyppeteer~=2.0.0",
        "pyyaml~=6.0.2",
        "packaging~=24.0.0",
        "qrcode~=8.0",
        "qrcode-terminal~=0.8",
        "gitpython~=3.1.44",
        "schedule~=1.2.2",
        "deprecated~=1.2.12",
    ],
)
