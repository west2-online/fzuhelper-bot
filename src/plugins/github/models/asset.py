from typing import Optional

from pydantic import BaseModel


class Asset(BaseModel):
    url: str
    id: int
    node_id: str
    name: str
    label: Optional[str] = None
    content_type: Optional[str] = None
    state: Optional[str] = None
    size: Optional[int] = None
    download_count: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    browser_download_url: Optional[str] = None