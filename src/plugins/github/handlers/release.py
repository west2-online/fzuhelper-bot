import asyncio

import aiohttp
import nonebot
from cachetools import TTLCache
from nonebot import get_plugin_config

from ..models import Release, Repository
from ..changelog import process_changelog
from ..config import Config
from ..github_proxy import GitHubProxy
from ..utils import upload_group_file, send_group_message

config = get_plugin_config(Config)
processed_releases = TTLCache(maxsize=100, ttl=60 * 60 * 12)


async def try_upload_apk():
    max_retries = 3
    retry_delay = 5

    await asyncio.sleep(retry_delay)

    for attempt in range(max_retries):
        try:
            api_url = f"https://api.github.com/repos/{config.app_repo}/releases/tags/alpha"
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url,
                                       headers={"Accept": "application/vnd.github+json"}) as resp:
                    resp.raise_for_status()
                    apiPayload = await resp.json()

            apiRelease = Release.model_validate(apiPayload)
            apk_asset = apiRelease.assets[0]
            apk_name = apk_asset.name.replace(".apk", ".Apk")
            file = await GitHubProxy.download_file(apk_asset.browser_download_url, True)
            await upload_group_file(config.test_group_id, apk_name, file)

            nonebot.logger.success(f"APK上传成功！(第{attempt + 1}次尝试)")
            break

        except Exception as e:
            nonebot.logger.error(f"第{attempt + 1}次尝试失败: {str(e)}")

            if attempt < max_retries - 1:
                nonebot.logger.info(f"{retry_delay}秒后重试...")
                await asyncio.sleep(retry_delay)
            else:
                nonebot.logger.warning(f"经过{max_retries}次尝试后仍然失败，放弃上传")


async def handle_release(payload: dict):
    action = payload["action"]
    repo = Repository.model_validate(payload['repository'])
    release = Release.model_validate(payload['release'])

    release_key = f"{release.id}_{action}"
    if release_key in processed_releases:
        nonebot.logger.info(f"忽略重复的release事件: {release_key}")
        return {"message": "duplicate ignored"}
    processed_releases[release_key] = True

    nonebot.logger.info(f"收到release事件({action}): {release.model_dump_json()}")
    if (repo.full_name == config.app_repo and
            action == "published" and
            release.tag_name == "alpha"):
        git_log = await process_changelog(release.body)

        message = (f"『{release.name}更新日志』\n" +
                   git_log)

        asyncio.create_task(send_group_message(config.test_group_id, message))
        asyncio.create_task(try_upload_apk())
        return {"message": "ok"}

    return {"message": "Not processed"}
