import os

from pydantic import BaseModel, Field


class Config(BaseModel):
    offline_notice_webhook: str = Field(default=os.getenv("OFFLINE_NOTICE_WEBHOOK", ""))