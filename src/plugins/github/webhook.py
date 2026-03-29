import asyncio
import json

import aiohttp
import nonebot
from fastapi import Request, HTTPException, FastAPI
from nonebot import get_plugin_config
from starlette import status

from .changelog import process_changelog
from .config import Config
from .github_proxy import GitHubProxy
from .models import Release, Repository
from .utils import verify_signature, send_group_message, upload_group_file

app: FastAPI = nonebot.get_app()
config = get_plugin_config(Config)


@app.post("/github/webhook")
async def _(request: Request):
    event_type = request.headers.get("X-GitHub-Event")
    signature = request.headers.get('X-Hub-Signature-256')
    if signature is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Required signature header is missing"
        )

    body = await request.body()
    if not verify_signature(body, signature, config.webhook_secret):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Signature verification failed, request may have been tampered with or secret is incorrect"
        )

    payload = json.loads(body.decode('utf-8'))
    repo = Repository.model_validate(payload['repository'])
    processed_releases = set()
    match event_type:
        case "release":
            action = payload["action"]
            release = Release.model_validate(payload['release'])

            release_key = f"{release.id}_{action}"
            if release_key in processed_releases:
                nonebot.logger.info(f"忽略重复的release事件: {release_key}")
                return {"message": "duplicate ignored"}
            processed_releases.add(release_key)

            nonebot.logger.info(f"收到release事件({action}): {release.model_dump_json()}")
            if (repo.full_name == config.app_repo and
                    action == "published" and
                    release.tag_name == "alpha"):
                git_log = await process_changelog(release.body)

                message = (f"『{release.name}更新日志』\n" +
                           git_log)

                asyncio.create_task(send_group_message(config.test_group_id,
                                                       message))

                async def try_upload_apk():
                    max_retries = 3
                    retry_delay = 5

                    await asyncio.sleep(retry_delay)

                    api_url = f"https://api.github.com/repos/{config.app_repo}/releases/tags/alpha"
                    async with aiohttp.ClientSession() as session:
                        async with session.get(api_url, headers={"Accept": "application/vnd.github+json"}) as resp:
                            resp.raise_for_status()
                            apiPayload = await resp.json()

                    apiRelease = Release.model_validate(apiPayload)
                    apk_asset = apiRelease.assets[0]
                    apk_name = apk_asset.name.replace(".apk", ".Apk")

                    for attempt in range(max_retries):
                        try:
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

                asyncio.create_task(try_upload_apk())
                return {"message": "ok"}

            return {"message": "Not processed"}

        case "ping":
            return {"message": "pong"}

        case _:
            return {"message": "Not processed"}


@app.get("/")
async def _():
    return {"message": "pong"}
