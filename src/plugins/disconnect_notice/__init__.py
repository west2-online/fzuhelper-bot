from nonebot.plugin import PluginMetadata

from . import notice_event

__plugin_meta__ = PluginMetadata(
    name="disconnect_notice",
    description="掉线时发送飞书通知",
    usage="...",
    type="plugin",
    supported_adapters={"~onebot.v11"},
    extra={
        "author": "Cai",
        "version": "0.0.1",
        "priority": 1,
    },
)