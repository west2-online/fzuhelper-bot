from nonebot import on_notice
from nonebot.adapters.onebot.v11 import NoticeEvent

from .feishu import post_offline_notice
from .models.bot_offline_notice import BotOfflineNotice

notice = on_notice()


@notice.handle()
async def _(event: NoticeEvent):
    if event.notice_type == "bot_offline":
        offline_notice = BotOfflineNotice.model_validate(event.model_dump())
        await post_offline_notice(offline_notice.self_id, offline_notice.message, offline_notice.tag)