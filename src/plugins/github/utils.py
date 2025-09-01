import hashlib
import hmac
from pathlib import Path

import aiohttp
import nonebot
from nonebot.adapters.onebot.v11 import Bot, Message

from ... import TEMP_DIR_PATH


async def send_group_message(group_id: int, message: str | Message):
    bot: Bot = nonebot.get_bot()
    await bot.send_group_msg(group_id=group_id, message=message)


async def upload_group_file(group_id: int, file_name: str, delete_after_upload: bool = True):
    bot: Bot = nonebot.get_bot()
    file_path = TEMP_DIR_PATH / file_name
    try:
        await bot.call_api("upload_group_file", group_id=group_id, file=str(file_path), name=file_name)
        '''
        /upload_group_file
        {
        "group_id": 0,
        "file": "string",
        "name": "string",
        "folder": "/"
        }
        '''
    finally:
        if delete_after_upload:
            file_path.unlink(missing_ok=True)


async def download_release_file(url: str, file_name: str, use_xget: bool = True):
    if use_xget:
        url = (url.replace("https://github.com/", "https://xget.xi-xu.me/gh/"))

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            file_path = TEMP_DIR_PATH / file_name

            with open(file_path, 'wb') as f:
                async for chunk in response.content.iter_chunked(1024):
                    f.write(chunk)


def verify_signature(payload, signature, secret) -> bool:
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    expected_signature = 'sha256=' + mac.hexdigest()
    return hmac.compare_digest(expected_signature, signature)


def format_git_log(release_body: str) -> str:
    git_log = "\n".join(
        release_body
        .strip()
        .splitlines()
        [:-1]).strip()

    commits = [commit.strip() for commit in git_log.split('\n\n') if commit.strip()]

    return '\n\n'.join(commits)
