import asyncio
import json

import nonebot
from cachetools import TTLCache
from fastapi import FastAPI, HTTPException, Request
from nonebot.adapters.qq import MessageSegment
from starlette import status

from .. import config
from ..changelog import process_changelog
from ..config import TestGroupConfig
from ..github import fetch_release, get_apk_version
from ..github_proxy import GitHubProxy
from ..model import Release, Repository
from ..review_react import add_pending
from ..utils import send_group_message, upload_group_file, verify_signature

app: FastAPI = nonebot.get_app()


@app.post("/github/webhook")
async def _(request: Request):
    event_type = request.headers.get("X-GitHub-Event")
    signature = request.headers.get("X-Hub-Signature-256")
    if signature is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Required signature header is missing",
        )

    body = await request.body()
    if not verify_signature(body, signature, config.webhook_secret):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Signature verification failed, request may have been tampered with or secret is incorrect",
        )

    payload = json.loads(body.decode("utf-8"))

    match event_type:
        case "release":
            return await handle_release(payload)
        case "ping":
            return handle_ping()
        case _:
            return {"message": "Not processed"}


async def try_upload_apk(release: Release, group_openid: str) -> None:
    """下载 release 里的 apk 并上传到群，失败时重试。"""
    max_retries = 3
    retry_delay = 5

    await asyncio.sleep(retry_delay)

    for attempt in range(max_retries):
        try:
            apk_asset = release.assets[0]
            apk_name = apk_asset.name.replace(".apk", ".Apk")
            file = await GitHubProxy.download_file(apk_asset.browser_download_url, True)
            await upload_group_file(group_openid, apk_name, file)

            nonebot.logger.success(f"APK上传成功！(第{attempt + 1}次尝试)")
            break

        except Exception as e:  # noqa: BLE001
            nonebot.logger.error(f"第{attempt + 1}次尝试失败: {e!s}")

            if attempt < max_retries - 1:
                nonebot.logger.info(f"{retry_delay}秒后重试...")
                await asyncio.sleep(retry_delay)
            else:
                nonebot.logger.warning(f"经过{max_retries}次尝试后仍然失败，放弃上传")


processed_releases: TTLCache[str, bool] = TTLCache(maxsize=100, ttl=60 * 60 * 12)  # type: ignore

# 持有推送任务的强引用，否则事件循环只持弱引用，任务可能在执行途中被 GC 回收
background_tasks: set[asyncio.Task] = set()


async def handle_release(payload: dict):
    action = payload["action"]
    repo = Repository.model_validate(payload["repository"])
    release = Release.model_validate(payload["release"])

    release_key = f"{release.id}_{action}"
    if release_key in processed_releases:
        nonebot.logger.info(f"忽略重复的 release 事件: {release_key}")
        return {"message": "duplicate ignored"}
    processed_releases[release_key] = True

    nonebot.logger.info(f"收到 release 事件({action}): {release.model_dump_json()}")
    if (
        repo.full_name == config.app_repo
        and action == "published"
        and release.tag_name == "alpha"
    ):
        git_log = await process_changelog(release.body)

        message = MessageSegment.markdown(f"## ⬆️ {release.name} 更新日志\n" + git_log)

        async def publish(test_group: TestGroupConfig):
            try:
                await send_group_message(test_group.test_group_openid, message)
                alpha_release = await fetch_release(config.app_repo, "alpha")
                version = get_apk_version(alpha_release)

                if test_group.push_android:
                    await try_upload_apk(alpha_release, test_group.test_group_openid)

                if test_group.push_apple and version is not None:
                    add_pending(test_group.test_group_openid, version, "apple")

                if test_group.push_harmony and version is not None:
                    add_pending(test_group.test_group_openid, version, "huawei")
            except Exception:  # noqa: BLE001
                nonebot.logger.exception(
                    f"推送测试群 {test_group.test_group_openid} 失败"
                )

        for test_group in config.test_groups:
            task = asyncio.create_task(publish(test_group))
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)

        return {"message": "ok"}

    return {"message": "Not processed"}


def handle_ping():
    return {"message": "pong"}
