from typing import Optional

from pydantic import BaseModel


class Asset(BaseModel):
    url: str
    id: int
    node_id: str
    name: str
    label: str | None = None
    content_type: str | None = None
    state: str | None = None
    size: int | None = None
    download_count: int | None = None
    created_at: str | None = None
    updated_at: str | None = None
    browser_download_url: str
