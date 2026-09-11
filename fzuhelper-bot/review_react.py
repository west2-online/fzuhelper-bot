from dataclasses import dataclass
from typing import Literal

import nonebot
from nonebot import get_plugin_config
from nonebot.adapters.qq import Bot, MessageSegment
from nonebot_plugin_apscheduler import scheduler

from . import app_gallery, app_store
from .app_gallery.model import Credentials
from .config import Config
from .keyboard import app_test_keyboard, test_flight_keyboard


@dataclass
class PendingReview:
    group_openid: str
    review_type: Literal["huawei", "apple", "done"]
    version: str


pending_reviews: list[PendingReview] = []


def add_pending(group_openid: str, version: str, type: Literal["huawei", "apple"]):
    pending_reviews.append(
        PendingReview(
            group_openid=group_openid,
            review_type=type,
            version=version,
        )
    )


config = get_plugin_config(Config)


async def react_msg(
    group_openid: str, react_type: Literal["huawei", "apple"], version: str
):
    bot: Bot = nonebot.get_bot()  # type: ignore

    if react_type == "huawei":
        message = (
            MessageSegment.markdown(f"🌼 Harmony（{version}）已通过 AppTest 测试审核！")
            + app_test_keyboard
        )
    else:
        message = (
            MessageSegment.markdown(f"🍎 iOS（{version}）已通过 TestFlight 测试审核！")
            + test_flight_keyboard
        )

    await bot.send_to_group(group_openid=group_openid, message=message)


@scheduler.scheduled_job("cron", minute="*", id="review_state_update")
async def update():
    global pending_reviews

    if len(pending_reviews) == 0:
        return

    huawei_client = app_gallery.AppGalleryClient(
        Credentials.model_validate(config.app_gallery_credentials),
        str(config.app_gallery_app_id),
    )
    huawei_versions = await huawei_client.query_ready_test_version()

    apple_client = app_store.build_client(
        config.app_store_issuer_id,
        config.app_store_key_id,
        config.app_store_key_contents,
    )
    apple_versions = app_store.query_ready_test_version(
        apple_client, str(config.app_store_app_id)
    )

    for i in pending_reviews:
        if i.review_type == "huawei" and i.version in huawei_versions:
            i.review_type = "done"
            await react_msg(i.group_openid, "huawei", i.version)

        if i.review_type == "apple" and i.version in apple_versions:
            i.review_type = "done"
            await react_msg(i.group_openid, "apple", i.version)

    pending_reviews = [x for x in pending_reviews if x.review_type != "done"]
