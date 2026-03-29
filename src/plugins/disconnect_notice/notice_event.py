from nonebot import on_notice
from nonebot.adapters.milky.event import BotOfflineEvent

from .email import post_email_offline_notice
from .feishu import post_feishu_offline_notice

notice = on_notice()


@notice.handle()
async def _(event: BotOfflineEvent):
    await post_feishu_offline_notice(event.self_id, event.data.reason)
    await post_email_offline_notice(event.self_id, event.data.reason)