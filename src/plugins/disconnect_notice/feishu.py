import aiohttp
import nonebot
from nonebot import get_plugin_config

from .config import Config

config = get_plugin_config(Config)


async def post_offline_notice(qq: int, msg: str, reason: str) -> None:
    async with aiohttp.ClientSession() as session:
        payload = {
            "msg": msg,
            "reason": reason,
            "qq": qq
        }
        async with session.post(config.offline_notice_webhook, json=payload) as response:
            if response.status == 200:
                nonebot.logger.success("Bot掉线上报成功!")
            else:
                nonebot.logger.error(f"Bot掉线上报失败!\n"
                                     f"WebHook响应: {response.text()}")
