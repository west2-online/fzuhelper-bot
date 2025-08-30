from pydantic import BaseModel


class BotOfflineNotice(BaseModel):
    self_id: int
    post_type: str
    notice_type: str
    tag: str
    message: str