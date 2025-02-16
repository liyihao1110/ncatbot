import requests

from ncatbot.utils.logger import get_log

_log = get_log()


def get_proxy_url():
    """获取 github 代理 URL"""
    github_proxy_urls = [
        "https://github.7boe.top/",
        "https://cdn.moran233.xyz/",
        "https://gh-proxy.ygxz.in/",
        "https://gh-proxy.lyln.us.kg/",
        "https://github.whrstudio.top/",
        "https://proxy.yaoyaoling.net/",
        "https://ghproxy.net/",
        "https://fastgit.cc/",
        "https://git.886.be/",
        "https://gh-proxy.com/",
        "https://ghfast.top/",
    ]
    _log.info("正在尝试连接 GitHub 代理...")
    for url in github_proxy_urls:
        try:
            _log.info(f"正在尝试连接 {url}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return url
        except requests.RequestException as e:
            _log.info(f"无法连接到 {url}: {e}, 继续尝试下一个代理...")
            continue
    _log.info("无法连接到任何 GitHub 代理, 将直接连接 GitHub")
    return ""


def get_version(github_proxy_url: str):
    """从GitHub获取 napcat 版本号"""
    version_url = f"{github_proxy_url}https://raw.githubusercontent.com/NapNeko/NapCatQQ/main/package.json"
    version_response = requests.get(version_url)
    if version_response.status_code == 200:
        version = version_response.json()["version"]
        _log.info(f"获取最新版本信息成功, 版本号: {version}")
        return version
    _log.info(f"获取最新版本信息失败, http 状态码: {version_response.status_code}")
    return None
