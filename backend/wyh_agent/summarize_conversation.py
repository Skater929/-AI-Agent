import json
from dotenv import load_dotenv
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    # 手动抛出（触发）异常，中断正常流程
    raise EnvironmentError("未设置 DEEPSEEK_API_KEY 环境变量")

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")


def summarize_conversation(conversation_history):
    # 把 [{"role": "user", "content": "..."}] 这种格式转成纯文本
    dialogue_text = "\n".join([msg["content"] for msg in conversation_history])
    system_prompt = """

    你是一个专业的对话数据提取与摘要助手。
    请根据用户的对话内容，严格按照以下 JSON Schema 格式提取信息并返回。
    注意：必须只返回纯净的 JSON 字符串，不要包含任何 Markdown 标记（如 ```json ... ```）或其他解释性文字。
{
    "long_term_memory": "一句话精简概括本次对话的核心事件，不超过 50 字。",
    "active_tasks_active": ["提取到的待办任务1", "提取到的待办任务2"],
    "preferences": ["提取到的用户新偏好1", "提取到的用户新偏好2"]
}
如果没有任务或偏好，对应字段返回空列表 []。
"""

    response = client.chat.completions.create(
        model="deepseek-chat",  # 使用标准 chat 模型，JSON Mode 兼容性更好
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": dialogue_text},
        ],
        response_format={"type": "json_object"},  # 强制开启结构化 JSON 输出
        extra_body={"thinking": {"type": "disabled"}},
    )
    # 4. 安全解析 JSON 并返回 Python 字典
    json_content = response.choices[0].message.content
    try:
        return json.loads(json_content)
    except json.JSONDecodeError:
        return {"long_term_memory": "", "active_tasks_active": [], "preferences": []}
