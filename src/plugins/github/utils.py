import hashlib
import hmac

import nonebot
from nonebot.adapters.milky import Bot, Message


async def send_group_message(group_id: int, message: str | Message) -> None:
    bot: Bot = nonebot.get_bot()
    await bot.send_group_message(group_id=group_id, message=message)


async def upload_group_file(group_id: int, file_name: str, file: bytes) -> None:
    bot: Bot = nonebot.get_bot()
    await bot.upload_group_file(group_id=group_id, raw=file, file_name=file_name)


def verify_signature(payload, signature, secret) -> bool:
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    expected_signature = 'sha256=' + mac.hexdigest()
    return hmac.compare_digest(expected_signature, signature)
