import hashlib
import hmac

import nonebot
from nonebot.adapters.qq import Bot, Message, MessageSegment


async def send_group_message(
    group_openid: str, message: str | Message | MessageSegment
) -> None:
    bot: Bot = nonebot.get_bot()  # type: ignore
    await bot.send_to_group(group_openid=group_openid, message=message)


async def upload_group_file(group_openid: str, file_name: str, file: bytes) -> None:
    bot: Bot = nonebot.get_bot()  # type: ignore
    await bot.send_to_group(
        group_openid=group_openid,
        message=MessageSegment.file_file(data=file, file_name=file_name),
    )


def verify_signature(payload, signature, secret) -> bool:
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected_signature, signature)
