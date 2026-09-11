from nonebot.plugin import PluginMetadata, get_plugin_config

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="fzuhelper-bot",
    description="福uu测试群发changelog的插件和安装包",
    usage="...",
    type="plugin",
    config=Config,
    supported_adapters={"~qq"},
)

config: Config = get_plugin_config(Config)

from . import (
    api,
    command,
    review_react,
)

__all__ = ["api", "command", "config", "review_react"]
