from nonebot import on_command

ping = on_command("bot-ping", force_whitespace=True, block=True)


@ping.handle()
async def _():
    await ping.finish("pong")
