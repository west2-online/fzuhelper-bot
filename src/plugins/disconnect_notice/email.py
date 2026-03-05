from email.message import EmailMessage

import aiosmtplib
import nonebot
from nonebot import get_plugin_config
from .config import Config

config = get_plugin_config(Config)

HTML_TEMPLATE = """
<html>
<body style="font-family: 'Microsoft YaHei', sans-serif; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
        <div style="background-color: #ff4d4f; color: white; padding: 20px; text-align: center;">
            <h2 style="margin: 0;">⚠️Bot离线上报</h2>
        </div>
        <div style="padding: 20px; line-height: 1.6;">
            <p>机器人已掉线，请及时检查服务状态。</p>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px 0; color: #888; width: 100px;">QQ</td>
                    <td style="padding: 10px 0; font-weight: bold;">{qq}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; color: #888; width: 100px;">消息</td>
                    <td style="padding: 10px 0; font-weight: bold;">{msg}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; color: #888;">原因</td>
                    <td style="padding: 10px 0; color: #cf1322;">{reason}</td>
                </tr>
            </table>
        </div>
    </div>
</body>
</html>
"""


async def post_email_offline_notice(qq: int, msg: str, reason: str) -> None:
    if (not config.smtp_server or config.smtp_port == 0 or not config.smtp_username or not config.smtp_password or
            not config.email_to or not config.email_from):
        nonebot.logger.info("SMTP配置不完整，跳过邮件上报掉线!")
        return

    content = HTML_TEMPLATE.format(qq=qq, msg=msg, reason=reason)

    message = EmailMessage()
    message["From"] = config.email_from
    message["To"] = config.email_to
    message["Subject"] = "机器人掉线通知"
    message.add_alternative(content, subtype="html")

    try:
        async with aiosmtplib.SMTP(
                hostname=config.smtp_server,
                port=config.smtp_port,
                use_tls=config.smtp_port == 465,
        ) as smtp:
            await smtp.login(config.smtp_username, config.smtp_password)
            await smtp.send_message(message)

        nonebot.logger.info(f"已成功向[{config.email_to}]发送掉线告警邮件。")
    except Exception as e:
        nonebot.logger.error(f"发送掉线邮件失败: {e}")
