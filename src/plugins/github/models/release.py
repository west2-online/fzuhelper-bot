from datetime import datetime

from pydantic import BaseModel, HttpUrl

from .asset import Asset


class Release(BaseModel):
    """GitHub release model"""

    id: int
    url: HttpUrl
    assets_url: HttpUrl
    upload_url: HttpUrl
    html_url: HttpUrl
    tag_name: str
    name: str
    draft: bool
    prerelease: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    published_at: datetime | None = None
    body: str
    assets: list[Asset]
