import time

import httpx
import jwt

from .model import (
    Credentials,
    ReleaseState,
    ReleaseType,
    VersionBriefInfo,
    VersionBriefInfoListResponse,
)

VERSION_BRIEF_INFO_LIST_URL = (
    "https://connect-api.cloud.huawei.com/api/publish/v3/version/brief-info/list"
)


def sign_service_account_jwt(credentials: Credentials) -> str:
    """Create the signed JWT used to obtain an AppGallery Connect access token."""
    now = int(time.time())
    payload = {
        "aud": credentials.token_uri,
        "iss": credentials.sub_account,
        "iat": now,
        "exp": now + 3600,
    }
    return jwt.encode(
        payload,
        credentials.private_key.replace("\\n", "\n"),
        algorithm="PS256",
        headers={"kid": credentials.key_id},
    )


async def query_version_brief_info_list(
    token: str,
    app_id: str,
    package_name: str | None = None,
    state: int | None = None,
    *,
    timeout: float = 30.0,
) -> list[VersionBriefInfo]:
    """Query version brief information and validate only supported fields."""
    body: dict[str, str | int] = {}
    if package_name is not None:
        body["packageName"] = package_name
    if state is not None:
        body["state"] = state

    headers = {
        "Authorization": f"Bearer {token}",
        "appId": app_id,
    }
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            VERSION_BRIEF_INFO_LIST_URL,
            headers=headers,
            json=body,
        )
        response.raise_for_status()
        payload = response.json()

    ret = payload.get("ret", {})
    if ret.get("code") != 0:
        raise RuntimeError(
            f"AppGallery Connect API error: {ret.get('msg', 'unknown error')}"
        )
    return VersionBriefInfoListResponse.model_validate(payload).versionList


async def query_ready_test_version(
    token: str,
    app_id: str,
    *,
    timeout: float = 30.0,
) -> list[str]:
    """Return the version codes of test releases currently online."""
    versions = await query_version_brief_info_list(token, app_id, timeout=timeout)
    return [
        str(pkg.versionCode)
        for version in versions
        if version.releaseType == ReleaseType.TEST
        and version.state == ReleaseState.ONLINE
        for pkg in version.packageList
    ]


class AppGalleryClient:
    """Service-account client for AppGallery Connect publish APIs."""

    def __init__(
        self,
        credentials: Credentials,
        app_id: str,
        *,
        timeout: float = 30.0,
    ) -> None:
        self.credentials = credentials
        self.app_id = app_id
        self.timeout = timeout

    async def query_version_brief_info_list(
        self,
        package_name: str | None = None,
        state: int | None = None,
    ) -> list[VersionBriefInfo]:
        token = sign_service_account_jwt(self.credentials)
        return await query_version_brief_info_list(
            token,
            self.app_id,
            package_name,
            state,
            timeout=self.timeout,
        )

    async def query_ready_test_version(self) -> list[str]:
        token = sign_service_account_jwt(self.credentials)
        return await query_ready_test_version(
            token,
            self.app_id,
            timeout=self.timeout,
        )
