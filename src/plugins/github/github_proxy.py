import re
import aiohttp
import nonebot.log

XGET_BASE = "https://xget.xi-xu.me/gh/"
GITHUB_URL_RE = re.compile(r"https://github\.com/(.+)")

PROXYS = [
    "https://ghproxy.net/",
    "https://gh.llkk.cc/",
    "https://gh-proxy.com/"
]


def _build_xget_url(github_url: str) -> str | None:
    m = GITHUB_URL_RE.match(github_url)
    if m:
        return XGET_BASE + m.group(1)
    return None


class GitHubProxy:
    current_proxy_index: int = 0

    @classmethod
    async def download_file(cls, url: str, use_proxy: bool = True) -> bytes:
        if not use_proxy:
            return await cls._do_download(url)

        xget_url = _build_xget_url(url)
        if xget_url:
            try:
                return await cls._do_download(xget_url)
            except Exception as e:
                nonebot.log.logger.info(f"xget下载失败，尝试其他代理: {str(e)}")

        tried = 0
        while tried < len(PROXYS):
            proxy_url = PROXYS[cls.current_proxy_index] + url
            try:
                return await cls._do_download(proxy_url)
            except Exception as e:
                print(f"通过代理 {PROXYS[cls.current_proxy_index]} 下载失败: {str(e)}")
                cls.current_proxy_index = (cls.current_proxy_index + 1) % len(PROXYS)  # 环形队列
                tried += 1
        raise Exception("所有代理下载失败")

    @classmethod
    async def _do_download(cls, url: str) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.read()
