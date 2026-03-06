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
你现在需要处理一段Git提交历史，将其转换为用户友好的更新日志。请按以下要求操作：

- 删除冗余信息（如提交哈希、合并记录、自动生成的元数据等）。
- 若提交信息包含英文，请翻译为简洁准确的中文。
- 忽略Co-authored-by、Closes、Fixes、Signed-off-by等标准Git尾注。
- 排除与CI/CD相关的内容，例如[skip ci]、[ci skip]、[build]等标记。
- 遇到无关链接时，直接删除整段链接，不保留文字或URL。
- 严格保留原始提交意图，不得添加未提及内容。
- 尽量简洁；若原提交信息已清晰，无需额外说明。
- 若单条提交包含多项具体改动，在主日志条目下以“•”列出，每项一行，并缩进四个空格。
- 各改动之间空一行。
- 只有三个提交，你只能按顺序输出三个日志条目，不能添加或删除条目。
- 输出纯文本，不使用Markdown、标题、代码块或其他格式。
- 最终输出格式如下：

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
