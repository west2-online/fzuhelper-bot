import os

from pydantic import BaseModel, Field


class Config(BaseModel):
    webhook_secret: str = Field(default=os.getenv("WEBHOOK_SECRET", ""))
    test_group_id: int = Field(default=int(os.getenv("TEST_GROUP_ID", "0")))
    app_repo: str = Field(default=os.getenv("APP_REPO", ""))