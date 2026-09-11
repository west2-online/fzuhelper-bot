import re

import httpx
import nonebot
from nonebot import get_plugin_config

from .config import Config

config = get_plugin_config(Config)


def format_git_log(release_body: str) -> str:
    git_log = "\n".join(release_body.strip().splitlines()[:-1]).strip()

    commits = [commit.strip() for commit in git_log.split("\n\n") if commit.strip()]

    return "\n\n".join(commits)


CHANGELOG_PROMPT = """
你是一个专业的版本发布日志（Changelog）生成助手。你的唯一任务是将用户提供的 Git 提交历史，严格按照下列规则转换为中文更新日志，不得有任何偏差。

【第一步：信息过滤（处理前必须执行）】

在转换前，先从原始提交信息中删除以下所有内容：
- CI/CD标记（如 [skip ci]、[build]、[no ci] 等）
- 所有URL链接及其附带文字，整段删除
- Conventional Commits前缀（如 feat:、fix:、build(deps): 等）

【第二步：翻译与润色】

- 将剩余英文内容准确翻译为简练中文
- 严格保持原意，绝不添加、推断或捏造原文未提及的信息
- 若原文已是清晰中文，保持不变，仅做必要润色
- 如果是平台专属更改，前面应该加上 对应平台： 前缀，其他情况不加前缀
- 注意要保留PR编号（如 #382）

【输出格式（不可更改）】

- 条目数量必须与输入完全一致，不得增加或删减
- 按原始顺序输出
- 编号格式为"数字. "（数字后跟英文句点和一个空格）
- 每个条目之间空一行

【格式模板】

1. 条目一

2. 条目二

3. 条目三

【示例】

输入：
1. add dark mode support (#382)
2. fix(android): resolve crash on startup https://github.com/xxx/xxx/issues/123
3. build(deps): bump lodash from 4.17.20 to 4.17.21 [skip ci]
4. chore: 优化构建速度
5. feat(ios): support live activities
6. feat(harmony): 支持锁屏小组件

输出：
1. 添加深色模式支持

2. Android：修复启动时崩溃的问题

3. 升级 lodash 依赖版本

4. 优化构建速度

5. iOS：支持实时活动

6. Harmony：支持锁屏小组件
"""


async def call_model_process_changelog(prompt):
    headers = {
        "Authorization": f"Bearer {config.ai_api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": config.ai_model,
        "messages": [
            {"role": "system", "content": CHANGELOG_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
    }

    try:
        nonebot.logger.debug(
            f"AI 请求参数: model={config.ai_model}, url={config.ai_api_url}"
        )
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config.ai_api_url, headers=headers, json=data, timeout=60.0
            )
            response.raise_for_status()

            result = response.json()
            content: str = result["choices"][0]["message"]["content"]
            return content.strip()
    except httpx.HTTPStatusError as e:
        nonebot.logger.error(
            f"AI 请求HTTP错误: {e.response.status_code}, {e.response.text[:300]}"
        )
        raise
    except Exception as e:
        nonebot.logger.error(f"AI 请求异常: {type(e).__name__}: {e!s}")
        raise


async def process_changelog(changelog: str) -> str:
    formatted = format_git_log(changelog)

    if not all([config.ai_api_url, config.ai_model, config.ai_api_key]):
        nonebot.logger.warning("AI 模型配置不完整，跳过AI处理更新日志!")
        return formatted

    nonebot.logger.info("开始调用 AI 模型处理更新日志...")
    try:
        formatted = await call_model_process_changelog(formatted)
        nonebot.logger.success("AI 处理成功")
    except Exception as e:  # noqa: BLE001
        nonebot.logger.error(
            f"调用 AI 模型失败，退回原始更新日志: {type(e).__name__}: {e}"
        )

    return re.sub(
        r"\(#(\d+)\)",
        f"([#\\1](https://github.com/{config.app_repo}/pull/\\1))",
        formatted,
    )
