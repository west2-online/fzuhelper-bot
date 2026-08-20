from dataclasses import dataclass
from typing import Literal

import nonebot
from nonebot import get_plugin_config
from nonebot.adapters.milky import Bot
from nonebot_plugin_apscheduler import scheduler

from . import app_gallery, app_store
from .app_gallery.model import Credentials
from .config import Config


@dataclass
class PendingReview:
    group_id: int
    msg_id: int
    review_type: Literal["huawei", "apple", "done"]
    version: str


pending_reviews: list[PendingReview] = []


def add_pending(group_id: int, msg_id: int, version: str):
    pending_reviews.append(
        PendingReview(
            group_id=group_id,
            msg_id=msg_id,
            review_type="huawei",
            version=version,
        )
    )
    pending_reviews.append(
        PendingReview(
            group_id=group_id,
            msg_id=msg_id,
            review_type="apple",
            version=version,
        )
    )


config = get_plugin_config(Config)


async def react_msg(
    group_id: int, message_id: int, react_type: Literal["huawei", "apple"]
):
    bot: Bot = nonebot.get_bot()  # type: ignore

    await bot.send_group_message_reaction(
        group_id=group_id,
        message_seq=message_id,
        reaction="11093" if react_type == "huawei" else "127822",
        reaction_type="emoji",
    )


@scheduler.scheduled_job("cron", minute="*", id="review_state_update")
async def update():
    global pending_reviews
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
            await react_msg(i.group_id, i.msg_id, "huawei")

        if i.review_type == "apple" and i.version in apple_versions:
            i.review_type = "done"
            await react_msg(i.group_id, i.msg_id, "apple")

    pending_reviews = [x for x in pending_reviews if x.review_type != "done"]
