from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from .asset import Asset


class Release(BaseModel):
    """GitHub release model"""
    url: HttpUrl
    assets_url: HttpUrl
    upload_url: HttpUrl
    html_url: HttpUrl
    tag_name: str
    name: str
    draft: bool
    prerelease: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    body: Optional[str]
    assets: List[Asset]
