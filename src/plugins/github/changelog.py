import httpx
import nonebot
from nonebot import get_plugin_config

from .config import Config

config = get_plugin_config(Config)


def format_git_log(release_body: str) -> str:
    git_log = "\n".join(
        release_body
        .strip()
        .splitlines()
        [:-1]).strip()

    commits = [commit.strip() for commit in git_log.split('\n\n') if commit.strip()]

    return '\n\n'.join(commits)


CHANGELOG_PROMPT = """
你是一个专业的版本发布日志（Changelog）生成助手。你的唯一任务是将用户提供的Git提交历史，严格按照下列规则转换为中文更新日志，不得有任何偏差。

【第一步：信息过滤（处理前必须执行）】

在转换前，先从原始提交信息中删除以下所有内容：
- PR编号（如 #382）、提交哈希
- 合并提交记录（如 Merge pull request...）
- CI/CD标记（如 [skip ci]、[build]、[no ci] 等）
- 所有URL链接及其附带文字，整段删除
- Git尾注（Co-authored-by / Closes / Fixes / Signed-off-by 等），整行删除
- Conventional Commits前缀（如 feat:、fix:、build(deps): 等），直接去掉

【第二步：翻译与润色】

- 将剩余英文内容准确翻译为简练中文
- 严格保持原意，绝不添加、推断或捏造原文未提及的信息
- 若原文已是清晰中文，保持不变，仅做必要润色

【第三步：排版（逐条强制检查）】

空格规则——这是最高优先级规则，输出前必须逐字检查：
中文字符与任何英文字母、数字、半角标点之间，绝对禁止出现空格。

错误：更新 tar 到 3.1.1
正确：更新tar到3.1.1

错误：支持 OAuth2 登录
正确：支持OAuth2登录

【输出格式（不可更改）】

- 纯文本输出，绝对禁止使用任何Markdown语法（无#标题、无**加粗**、无代码块、无列表符号-或*）
- 条目数量必须与输入完全一致，不得增加或删减
- 按原始顺序输出
- 编号格式为"数字. "（数字后跟英文句点和一个空格）
- 每个条目之间空一行

【格式模板】

1. 条目一

2. 条目二

3. 条目三

【自检要求】

输出前，请默默完成以下检查，不要将检查过程输出给用户：
1. 是否有任何中文与英文/数字之间存在空格？若有，立即修正。
2. 条目数量是否与输入一致？
3. 是否混入了任何Markdown符号？

确认无误后，仅输出最终日志，不输出任何解释、前言或结语。
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
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
    }

    try:
        nonebot.logger.debug(f"AI请求参数: model={config.ai_model}, url={config.ai_api_url}")
        async with httpx.AsyncClient() as client:
            response = await client.post(config.ai_api_url, headers=headers, json=data, timeout=60.0)
            response.raise_for_status()

            result = response.json()
            content: str = result['choices'][0]['message']['content']
            return content.strip()
    except httpx.HTTPStatusError as e:
        nonebot.logger.error(f"AI请求HTTP错误: {e.status_code}, {e.response.text[:300]}")
        raise
    except Exception as e:
        nonebot.logger.error(f"AI请求异常: {type(e).__name__}: {str(e)}")
        raise


async def process_changelog(changelog: str) -> str:
    formated_changelog = format_git_log(changelog)

    # 检查AI配置
    has_url = bool(config.ai_api_url)
    has_model = bool(config.ai_model)
    has_key = bool(config.ai_api_key)
    nonebot.logger.info(f"AI配置检查: url={has_url}, model={has_model}, key={has_key}")
    
    if not config.ai_api_url or not config.ai_model or not config.ai_api_key:
        nonebot.logger.warning(f"AI模型配置不完整，跳过AI处理更新日志! (url={has_url}, model={has_model}, key={has_key})")
        return formated_changelog

    nonebot.logger.info("开始调用AI模型处理更新日志...")
    try:
        result = await call_model_process_changelog(formated_changelog)
        nonebot.logger.success("AI处理成功")
        return result
    except Exception as e:
        nonebot.logger.error(f"调用AI模型处理更新日志失败，退回原始更新日志: {type(e).__name__}: {str(e)}")
        return formated_changelog
