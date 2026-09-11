from nonebot.adapters.qq import MessageSegment
from nonebot.adapters.qq.models import (
    Action,
    Button,
    InlineKeyboard,
    InlineKeyboardRow,
    MessageKeyboard,
    Permission,
    RenderData,
)

from . import config

app_test_keyboard = MessageSegment.keyboard(
    MessageKeyboard(
        content=InlineKeyboard(
            rows=[
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            render_data=RenderData(
                                label="🧪 加入 AppTest",
                                visited_label="🧪 加入 AppTest",
                                style=1,
                            ),
                            action=Action(
                                type=0,
                                data=config.huawei_app_test_url,
                                permission=Permission(type=2),
                            ),
                        )
                    ]
                )
            ]
        )
    )
)


test_flight_keyboard = MessageSegment.keyboard(
    MessageKeyboard(
        content=InlineKeyboard(
            rows=[
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            render_data=RenderData(
                                label="✈️ 加入 TestFlight",
                                visited_label="✈️ 加入 TestFlight",
                                style=1,
                            ),
                            action=Action(
                                type=0,
                                data=config.apple_test_flight_url,
                                permission=Permission(type=2),
                            ),
                        )
                    ]
                )
            ]
        )
    )
)
