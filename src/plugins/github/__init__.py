from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="github",
    description="福uu测试群发changelog的插件和安装包",
    usage="...",
    type="plugin",
    supported_adapters={"~milky"},
    extra={
        "author": "Cai",
        "version": "1.0.0",
        "priority": 1,
    },
)

from . import webhook
from . import commands
