import os

from pydantic import BaseModel, Field


class Config(BaseModel):
    webhook_secret: str = Field(default=os.getenv("WEBHOOK_SECRET", ""))
    test_group_id: int = Field(default=int(os.getenv("TEST_GROUP_ID", "0")))
    app_repo: str = Field(default=os.getenv("APP_REPO", ""))

    ai_api_key: str = Field(default=os.getenv("AI_API_KEY", ""))
    ai_api_url: str = Field(default=os.getenv("AI_API_URL", ""))
    ai_model: str = Field(default=os.getenv("AI_MODEL", ""))

    # Apple App Store Connect API
    app_store_issuer_id: str = Field(default=os.getenv("APP_STORE_ISSUER_ID", ""))
    app_store_key_id: str = Field(default=os.getenv("APP_STORE_KEY_ID", ""))
    app_store_key_contents: str = Field(default=os.getenv("APP_STORE_KEY_CONTENTS", ""))
    app_store_app_id: int = Field(default=int(os.getenv("APP_STORE_APP_ID", "0")))

    # Huawei AppGallery Connect API
    app_gallery_credentials: dict = Field(default_factory=dict)
    app_gallery_app_id: int = Field(default=int(os.getenv("APP_GALLERY_APP_ID", "0")))
