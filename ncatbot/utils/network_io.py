import threading
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from tqdm import tqdm

from ncatbot.utils.logger import get_log
from ncatbot.utils.status import status

_log = get_log()


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
    TIMEOUT = 5
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
    result_queue = Queue(maxsize=1)

    def check_proxy(url):
        try:
            response = requests.get(url, timeout=TIMEOUT)
            if response.status_code == 200:
                result_queue.put(url)
        except TimeoutError as e:
            _log.warning(f"请求失败: {url}, 错误: {e}")

    with ThreadPoolExecutor(max_workers=10) as executor:
        for url in github_proxy_urls:
            executor.submit(check_proxy, url)
            for i in range(10):
                time.sleep(TIMEOUT / 10)
                if status.exit:
                    return
        executor._threads.clear()

    available_proxy = []
    try:
        while True:
            available_proxy.append(result_queue.get(block=True, timeout=0.1))
    except Exception:
        pass
    if len(available_proxy) > 0:
        status.current_github_proxy = available_proxy[0]
        return available_proxy[0]
    else:
        _log.warning("无法连接到任何 GitHub 代理, 将直接连接 GitHub")
        status.current_github_proxy = ""
        return ""


threading.Thread(target=get_proxy_url, daemon=True).start()

if __name__ == "__main__":

    print("done")
