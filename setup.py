from setuptools import find_packages, setup

setup(
    name="NcatBot",
    version="1.0.2",
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
    python_requires=">=3.12",
    install_requires=[
        "websockets~=10.4",
        "httpx~=0.28.1",
        "psutil~=6.1.1",
        "tqdm~=4.67.1",
        "requests~=2.32.3",
        "Markdown~=3.7",
        "Pygments~=2.19.1",
        "pyppeteer~=2.0.0",
    ],
)
