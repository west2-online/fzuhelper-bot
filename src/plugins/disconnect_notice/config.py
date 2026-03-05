import os

from pydantic import BaseModel, Field


class Config(BaseModel):
    offline_notice_webhook: str = Field(default=os.getenv("OFFLINE_NOTICE_WEBHOOK", ""))

    smtp_server: str = Field(default=os.getenv("SMTP_SERVER", ""))
    smtp_port: int = Field(default=int(os.getenv("SMTP_PORT", "0")))
    smtp_password: str = Field(default=os.getenv("SMTP_PASSWORD", ""))
    smtp_username: str = Field(default=os.getenv("SMTP_USERNAME", ""))
    email_to: str = Field(default=os.getenv("EMAIL_TO", ""))
    email_from: str = Field(default=os.getenv("EMAIL_FROM", ""))


