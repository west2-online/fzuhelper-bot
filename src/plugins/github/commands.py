import aiohttp

from nonebot import on_command, get_plugin_config
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from .changelog import process_changelog
from .config import Config
from .github_proxy import GitHubProxy
from .models import Release
from .utils import upload_group_file, send_group_message

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
    api_url = f"https://api.github.com/repos/{config.app_repo}/releases/tags/alpha"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers={"Accept": "application/vnd.github+json"}) as resp:
            resp.raise_for_status()
            payload = await resp.json()

    release = Release.model_validate(payload)

    apk_asset = release.assets[0]
    download_url: str = apk_asset.browser_download_url
    file_name: str = apk_asset.name.replace(".apk", ".Apk")

    await GitHubProxy.download_file(download_url, file_name, True)
    await upload_group_file(event.group_id, file_name)


changelog_test = on_command("bot-changelog", force_whitespace=True, block=True)


@changelog_test.handle()
async def _(event: GroupMessageEvent):
    api_url = f"https://api.github.com/repos/{config.app_repo}/releases/tags/alpha"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers={"Accept": "application/vnd.github+json"}) as resp:
            resp.raise_for_status()
            payload = await resp.json()

    release = Release.model_validate(payload)

    git_log = await process_changelog(release.body)

    message = (f"『{release.name}更新日志』\n" +
               git_log)

    await send_group_message(event.group_id, message)
    await changelog_test.finish()



