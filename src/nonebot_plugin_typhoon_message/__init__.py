from nonebot import logger, require, get_driver
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_uninfo")
require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")
require("nonebot_plugin_apscheduler")
from .config import Config
from .main import main

__plugin_meta__ = PluginMetadata(
    name="台风信息解析推送",
    description="爬取并解析中央气象台台风报文",
    usage="用法",
    type="application",  # library
    homepage="https://github.com/Leo-455/nonebot-plugin-typhoon-message",
    config=Config,
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_uninfo"
    ),
    # supported_adapters={"~onebot.v11"}, # 仅 onebot
    extra={"author": "Leo-455 Leo_455@163.com"},
)

from arclet.alconna import Args, Option, Alconna, Arparma, Subcommand
from nonebot_plugin_alconna import on_alconna
from nonebot_plugin_alconna.uniseg import UniMessage

pip = on_alconna(
    Alconna(
        "pip",
        Subcommand(
            "install",
            Args["package", str],
            Option("-r|--requirement", Args["file", str]),
            Option("-i|--index-url", Args["url", str]),
        ),
    )
)


@pip.handle()
async def _(result: Arparma):
    package: str = result.other_args["package"]
    logger.info(f"installing {package}")
    await UniMessage.text(package).send()


driver = get_driver()
@driver.on_startup
async def startup():
    logger.info("start")
    await main()
