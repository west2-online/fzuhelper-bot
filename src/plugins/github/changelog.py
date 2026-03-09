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
你是一个专业的版本发布日志（Changelog）生成助手。请将提供的Git提交历史转换为对用户友好的纯文本中文更新日志。

【核心处理规则】
信息清理：删除提交哈希、合并记录、自动生成的元数据、CI/CD相关标记（如 [skip ci]、[build] 等），以及无关链接（直接删除整段链接，不保留文字或URL）。
尾注过滤：忽略所有标准Git尾注（如 Co-authored-by, Closes, Fixes, Signed-off-by 等）。
翻译与润色：若包含英文，请准确翻译为简练的中文。严格保持原意，绝不捏造未提及的内容；若原提交信息已清晰，无需额外解释。
排版细节（严格执行）：
所有中文字符与相邻的英文字母、数字、半角符号之间严禁插入空格。
• 错误示例： 更新 tar 到 3.1.1（包含了空格）
• 正确示例： 更新tar到3.1.1（无任何空格）

【严格格式要求】
数量限制：必须按原始顺序严格处理并输出三个日志条目，不可增加或删减。
纯文本输出：绝对禁止使用任何Markdown语法（禁止使用代码块、标题符号#、加粗等），只输出纯文本。
层级排版：
主日志条目使用“数字. ”格式。
若单条提交包含多项具体改动，在主条目下方另起一行，使用“• ”列出，且必须精确缩进三个空格。
各主日志条目（包含其子项）之间必须空一行。

【最终输出格式示例】
1. 日志条目一  
   • 详细更改一  
   • 详细更改二  

2. 日志条目二  

3. 日志条目三  
   • 详细更改三
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

    async with httpx.AsyncClient() as client:
        response = await client.post(config.ai_api_url, headers=headers, json=data, timeout=60.0)
        response.raise_for_status()

        result = response.json()
        content: str = result['choices'][0]['message']['content']
        return content.strip()


async def process_changelog(changelog: str) -> str:
    formated_changelog = format_git_log(changelog)

    if not config.ai_api_url or not config.ai_model or not config.ai_api_key:
        nonebot.logger.info("AI模型配置不完整，跳过AI处理更新日志!")
        return formated_changelog

    try:
        return await call_model_process_changelog(formated_changelog)
    except Exception as e:
        nonebot.logger.error(f"调用AI模型处理更新日志失败，退回原始更新日志: {str(e)}")
        return formated_changelog
