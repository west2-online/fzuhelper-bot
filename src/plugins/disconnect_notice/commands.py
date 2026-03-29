from nonebot import on_command, get_plugin_config
from nonebot.adapters.milky import Bot
from .config import Config
from .email import post_email_offline_notice

email = on_command("bot-email-test", force_whitespace=True, block=True)

config = get_plugin_config(Config)


@email.handle()
async def _(bot: Bot):
    await post_email_offline_notice(qq=int(bot.self_id), reason="BOT假装掉线了...")
    await email.finish("测试邮件已发送!")
