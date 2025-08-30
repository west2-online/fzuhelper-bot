from nonebot import on_command, get_plugin_config
from .config import Config

ping = on_command("bot-ping", force_whitespace=True, block=True)

config = get_plugin_config(Config)
@ping.handle()
async def _():
    await ping.finish("pong\n"
                      f"app_repo: {config.app_repo}\n"
                      f"test_group_id: {config.test_group_id}")
