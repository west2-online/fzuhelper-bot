from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


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
    created_at: datetime
    updated_at: datetime
    published_at: datetime
    assets: List[dict]
    body: Optional[str]