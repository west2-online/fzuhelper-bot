import aiohttp

from ... import TEMP_DIR_PATH

PROXYS = [
    "https://ghproxy.net/",
    "https://gh.llkk.cc/",
    "https://gh-proxy.com/"
]


class GitHubProxy:
    current_proxy_index: int = 0

    @classmethod
    async def download_file(cls, url: str, file_name: str, use_proxy: bool = True):
        try:
            if use_proxy:
                url = PROXYS[cls.current_proxy_index] + url

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    file_path = TEMP_DIR_PATH / file_name

                    with open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(1024):
                            f.write(chunk)
        except:
            cls.current_proxy_index = (cls.current_proxy_index + 1) % len(PROXYS)  # 环形队列
            raise