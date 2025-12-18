from tqdm import tqdm
import socket
import json
import urllib
import urllib.request
import urllib.error

from ncatbot.utils.logger import get_log
from ncatbot.utils.status import status

_log = get_log()


def post_json(
    url: str,
    payload: dict | None = None,
    headers: dict | None = None,
    timeout: float = 5.0,
) -> dict:
    body = None
    req_headers = {
        "User-Agent": "ncatbot/1.0",
        "Accept": "application/json",
    }
    if headers:
        req_headers.update(headers)
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=req_headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", resp.getcode())
            if status != 200:
                raise urllib.error.HTTPError(
                    url, status, "Non-200 response", hdrs=resp.headers, fp=None
                )
            data = resp.read()
            return json.loads(data.decode("utf-8"))
    except socket.timeout as e:
        # 维持与原代码的 TimeoutError 语义一致
        raise TimeoutError("request timed out") from e
    except urllib.error.URLError as e:
        # 某些实现会把超时包裹在 URLError.reason 中
        if isinstance(getattr(e, "reason", None), socket.timeout):
            raise TimeoutError("request timed out") from e
        raise


def get_json(url: str, headers: dict | None = None, timeout: float = 5.0) -> dict:
    req_headers = {
        "User-Agent": "ncatbot/1.0",
        "Accept": "application/json",
    }
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", resp.getcode())
            if status != 200:
                raise urllib.error.HTTPError(
                    url, status, "Non-200 response", hdrs=resp.headers, fp=None
                )
            data = resp.read()
            return json.loads(data.decode("utf-8"))
    except socket.timeout as e:
        # 维持与原代码的 TimeoutError 语义一致
        raise TimeoutError("request timed out") from e
    except urllib.error.URLError as e:
        # 某些实现会把超时包裹在 URLError.reason 中
        if isinstance(getattr(e, "reason", None), socket.timeout):
            raise TimeoutError("request timed out") from e
        raise


def download_file(url, file_name):
    """下载文件, 带进度条"""
    try:
        import requests

        r = requests.get(url, stream=True)
        total_size = int(r.headers.get("content-length", 0))
        progress_bar = tqdm(
            total=total_size,
            unit="iB",
            unit_scale=True,
            desc=f"Downloading {file_name}",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            colour="green",
            dynamic_ncols=True,
            smoothing=0.3,
            mininterval=0.1,
            maxinterval=1.0,
        )
        with open(file_name, "wb") as f:
            for data in r.iter_content(chunk_size=1024):
                progress_bar.update(len(data))
                f.write(data)
        progress_bar.close()
    except Exception as e:
        _log.error(f"从 {url} 下载 {file_name} 失败")
        _log.error("错误信息:", e)
        return


def get_proxy_url():
    """获取 github 代理 URL"""
    import requests

    if status.current_github_proxy is not None:
        return status.current_github_proxy
    TIMEOUT = 10
    github_proxy_urls = [
        "https://ghfast.top/",
        # "https://github.7boe.top/",
        # "https://cdn.moran233.xyz/",
        # "https://gh-proxy.ygxz.in/",
        # "https://github.whrstudio.top/",
        # "https://proxy.yaoyaoling.net/",
        # "https://ghproxy.net/",
        # "https://fastgit.cc/",
        # "https://git.886.be/",
        # "https://gh-proxy.com/",
    ]
    available_proxy = []

    def check_proxy(url):
        try:
            response = requests.get(url, timeout=TIMEOUT)
            if response.status_code == 200:
                return url
        except TimeoutError as e:
            _log.warning(f"请求失败: {url}, 错误: {e}")
            return None
        except Exception:
            return None

    url = check_proxy(github_proxy_urls[0])
    if url is not None:
        available_proxy.append(url)

    if len(available_proxy) > 0:
        status.current_github_proxy = available_proxy[0]
        return available_proxy[0]
    else:
        _log.warning("无法连接到任何 GitHub 代理, 将直接连接 GitHub")
        status.current_github_proxy = None
        return ""


def gen_url_with_proxy(original_url: str) -> str:
    """生成带代理的 URL"""
    proxy_url = get_proxy_url()
    return (
        f"{proxy_url.strip('/')}/{original_url.strip('/')}"
        if proxy_url
        else original_url
    )


# threading.Thread(target=get_proxy_url, daemon=True).start()

if __name__ == "__main__":
    print("done")
