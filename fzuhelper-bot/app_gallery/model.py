from enum import IntEnum

from pydantic import BaseModel, ConfigDict


class ReleaseType(IntEnum):
    PUBLIC = 1
    TEST = 6


class ReleaseState(IntEnum):
    ONLINE = 0
    AUDIT_REJECTED = 1
    OFFLINE = 2
    PENDING = 3
    AUDITING = 4
    UPGRADE_AUDITING = 5
    APPLY_OFFLINE = 6
    DRAFT = 7
    UPGRADE_REJECTED = 8
    OFFLINE_REJECTED = 9
    OFFLINE_BY_DEV = 10
    WITHDRAWN = 11
    PRE_AUDITING = 12
    PRE_REJECTED = 13


class Credentials(BaseModel):
    model_config = ConfigDict()

    key_id: str
    private_key: str
    sub_account: str
    token_uri: str


class PackageBriefInfo(BaseModel):
    """Package info within a version's brief info.

    Only ``versionCode`` is required for our use; the rest is optional so a
    changed/partial response never fails validation.
    """

    model_config = ConfigDict()

    versionCode: int
    packageId: str | None = None
    versionName: str | None = None
    buildVersion: str | None = None


class VersionBriefInfo(BaseModel):
    """AppGallery Connect version brief information.

    ``versionCode`` (inside ``packageList``) is the only required field; every
    other field is optional so unknown or partial responses parse cleanly.
    """

    model_config = ConfigDict()

    versionId: str | None = None
    state: int | None = None
    releaseType: int | None = None
    packageList: list[PackageBriefInfo]


class VersionBriefInfoListResponse(BaseModel):
    model_config = ConfigDict()

    versionList: list[VersionBriefInfo]
