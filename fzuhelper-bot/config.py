from pydantic import BaseModel


class TestGroupConfig(BaseModel):
    test_group_openid: str
    push_android: bool
    push_apple: bool
    push_harmony: bool


class Config(BaseModel):
    webhook_secret: str
    app_repo: str
    test_groups: list[TestGroupConfig]

    ai_api_key: str
    ai_api_url: str
    ai_model: str

    # Apple App Store Connect API
    app_store_issuer_id: str
    app_store_key_id: str
    app_store_key_contents: str
    app_store_app_id: int

    # Huawei AppGallery Connect API
    app_gallery_credentials: dict
    app_gallery_app_id: int

    huawei_app_test_url: str
    apple_test_flight_url: str
