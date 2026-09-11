import re

import aiohttp

from .model import Release


async def fetch_release(repo: str, tag: str) -> Release:
    api_url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
    async with (
        aiohttp.ClientSession() as session,
        session.get(api_url, headers={"Accept": "application/vnd.github+json"}) as resp,
    ):
        resp.raise_for_status()
        apiPayload = await resp.json()

    return Release.model_validate(apiPayload)


def get_apk_version(release: Release) -> str | None:
    """从 release 的 apk 资源名中提取版本号。"""
    if not release.assets:
        return None

    matched = re.search(r"\.(\d+)\.apk", release.assets[0].name)
    return matched.group(1) if matched else None
