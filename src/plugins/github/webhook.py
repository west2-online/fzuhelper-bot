import json

import nonebot
from fastapi import Request, HTTPException, FastAPI
from nonebot import get_plugin_config
from starlette import status

from .config import Config
from .handlers.ping import handle_ping
from .handlers.release import handle_release
from .utils import verify_signature

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

    match event_type:
        case "release":
            return await handle_release(payload)
        case "ping":
            return handle_ping()
        case _:
            return {"message": "Not processed"}


@app.get("/")
async def _():
    return {"message": "pong"}
