import aiohttp

from nonebot import on_command, get_plugin_config
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from .config import Config
from .github_proxy import GitHubProxy
from .utils import upload_group_file

ping = on_command("bot-ping", force_whitespace=True, block=True)

config = get_plugin_config(Config)


@ping.handle()
async def _():
    await ping.finish("pong\n"
                      f"app_repo: {config.app_repo}\n"
                      f"test_group_id: {config.test_group_id}")


download_test = on_command("bot-download", force_whitespace=True, block=True)


@download_test.handle()
async def _(event: GroupMessageEvent):
    api_url = f"https://api.github.com/repos/west2-online/fzuhelper-app/releases/tags/alpha"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers={"Accept": "application/vnd.github+json"}) as resp:
            resp.raise_for_status()
            release = await resp.json()

    asset = release["assets"][0]
    download_url: str = asset["browser_download_url"]
    file_name: str = asset["name"].replace(".apk", ".Apk")

    await GitHubProxy.download_file(download_url, file_name, True)
    await upload_group_file(event.group_id, file_name)
