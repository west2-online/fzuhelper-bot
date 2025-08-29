from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="github",
    description="福uu测试群发changelog的插件 (目前是这样的)",
    usage="...",
    type="plugin",
    supported_adapters={"~onebot.v11"},
    extra={
        "author": "Cai",
        "version": "0.0.1",
        "priority": 1,
    },
)

from . import webhook
from . import commands