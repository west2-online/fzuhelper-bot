from nonebot.plugin import PluginMetadata

from . import notice_event
from . import commands

__plugin_meta__ = PluginMetadata(
    name="disconnect_notice",
    description="掉线时发送飞书通知/邮件通知",
    usage="...",
    type="plugin",
    supported_adapters={"~milky"},
    extra={
        "author": "Cai",
        "version": "1.0.0",
        "priority": 1,
    },
)