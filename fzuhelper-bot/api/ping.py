import nonebot
from fastapi import FastAPI

app: FastAPI = nonebot.get_app()


@app.get("/")
async def _():
    return {"message": "pong"}
