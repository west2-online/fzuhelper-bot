from nonebot import on_command
from nonebot.adapters.qq import Bot, GroupMessageCreateEvent, MessageSegment

from . import config
from .changelog import process_changelog
from .github import fetch_release, get_apk_version
from .github_proxy import GitHubProxy
from .review_react import add_pending
from .utils import send_group_message, upload_group_file

ping = on_command("bot-ping", force_whitespace=True, block=True)


@ping.handle()
async def _(event: GroupMessageCreateEvent):
    await ping.finish(
        MessageSegment.markdown(
            "## 🏓 pong\n"
            + f"- sender_openid: {event.author.member_openid}\n"
            + f"- group_openid: {event.group_openid}"
        )
    )


download_test = on_command("bot-download", force_whitespace=True, block=True)


@download_test.handle()
async def _(bot: Bot, event: GroupMessageCreateEvent):
    release = await fetch_release(config.app_repo, "alpha")

    apk_asset = release.assets[0]
    download_url: str = apk_asset.browser_download_url
    file_name: str = apk_asset.name.replace(".apk", ".Apk")

    file = await GitHubProxy.download_file(download_url, True)

    await upload_group_file(event.group_openid, file_name, file)


changelog_test = on_command("bot-changelog", force_whitespace=True, block=True)


@changelog_test.handle()
async def _(event: GroupMessageCreateEvent):
    release = await fetch_release(config.app_repo, "alpha")

    git_log = await process_changelog(release.body)

    message = MessageSegment.markdown(f"## ⬆️ {release.name} 更新日志\n" + git_log)
    await send_group_message(event.group_openid, message)

    version = get_apk_version(release)
    if version is not None:
        add_pending(event.group_openid, version, "apple")
        add_pending(event.group_openid, version, "huawei")
