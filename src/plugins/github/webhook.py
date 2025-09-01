import asyncio
import json

import nonebot
from fastapi import Request, HTTPException, FastAPI
from nonebot import get_plugin_config
from starlette import status

from .config import Config
from .models import Release, Repository
from .utils import verify_signature, send_group_message, format_git_log, download_release_file, upload_group_file

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
    match event_type:
        case "release":
            action = payload["action"]
            release = Release.model_validate(payload['release'])
            if (repo.full_name == config.app_repo and
                    action == "edited" and  # 只有edit才能拿到assets疑似工作流Bug
                    release.tag_name == "alpha"):
                git_log = format_git_log(release.body)

                message = (f"『{release.name}更新日志』\n" +
                           git_log)

                await send_group_message(config.test_group_id,
                                         message)

                async def upload_apk():
                    apk_asset = release.assets[0]
                    apk_name = apk_asset.name.replace(".apk", ".Apk")
                    await download_release_file(apk_asset.browser_download_url, apk_name, True)
                    await upload_group_file(config.test_group_id, apk_name)

                asyncio.create_task(upload_apk())
                return {"message": "ok"}

            return {"message": "Not processed"}

        case "ping":
            return {"message": "pong"}

        case _:
            return {"message": "Not processed"}


@app.get("/")
async def _():
    return {"message": "pong"}