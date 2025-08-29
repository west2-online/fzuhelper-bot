from ipaddress import ip_address

import nonebot
from fastapi import Request, HTTPException, FastAPI

app: FastAPI = nonebot.get_app()


@app.middleware("http")
async def check_network(request: Request, call_next):
    if request.url.path.startswith("/onebot"):
        ip = ip_address(request.client.host)
        if not (ip.is_private or ip.is_loopback):
            raise HTTPException(403)
    return await call_next(request)
