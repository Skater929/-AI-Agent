import json
import os
from pathlib import Path

import openai
from openai import OpenAI
from dotenv import load_dotenv

from backend.wyh_agent import summarize_conversation
import backend.wyh_agent.tool_schema as tool_schema
from backend.wyh_agent.function_calling.user_profile import (
    save_from_llm,
)

# 文件路径需要依据当前工作目录寻找
# ./当前目录内 ../上级目录
print("当前工作目录：", os.getcwd())
# ds_agent.py所在目录：backend/wyh_agent
BASE_DIR = Path(__file__).resolve().parent
# 向上两级：wyh_agent → backend → 项目根目录，再找同级的data
NOTES_PATH = BASE_DIR.parent.parent / "data" / "note.txt"

# 调试打印，运行看输出
print(f"note.txt完整路径: {NOTES_PATH}")
print(f"note.txt文件是否存在: {NOTES_PATH.is_file()}")

load_dotenv()

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
WEATHER_API_HOST = os.environ.get("API_HOST")

if not DEEPSEEK_API_KEY:
    # 手动抛出（触发）异常，中断正常流程
    raise EnvironmentError("未设置 DEEPSEEK_API_KEY 环境变量")

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# agent循环
# task: 用户输入的任务描述
# max_steps: 最大循环步数，防止无限调用工具
# 运行 Agent：通过"推理 → 调用工具 → 拿到结果 → 再推理"的循环完成任务
messages = []


def run_agent(task, messages, max_steps=8):
    # 用户消息
    messages.append({"role": "user", "content": task})
    for _ in range(max_steps):
        # 调用模型，传入工具列表，模型可选择直接回答或返回工具调用请求
        try:
            response = client.chat.completions.create(
                model="deepseek-flash",
                tools=tool_schema.TOOLS,
                messages=messages,
                extra_body={"thinking": {"type": "disabled"}},
            )
        except openai.AuthenticationError:
            messages.pop()
            # 直接退出循环，不浪费算力重试
            print("\n[致命错误] API Key 无效或已过期，请检查 .env 配置并重启程序。")
            return

        except openai.RateLimitError:
            messages.pop()
            print("\n[限流警告] 请求过于频繁，请稍后再试")
            return

        except openai.APIConnectionError as e:
            # 捕获网络连接错误
            print(f"\n[网络错误] 无法连接到服务器: {e}")
            print("请检查你的网络连接或防火墙设置。")
            messages.pop()
            return

        except openai.APIStatusError as e:
            # 捕获服务器错误 (如 500, 503 等)
            print(f"\n[服务器错误] DeepSeek 服务异常: {e}")
            print("服务器正忙，请稍后重新提问。")
            messages.pop()
            return
        except Exception as e:
            # 兜底：捕获其他所有未预料的错误
            print(f"\n[未知异常] 发生未定义的错误: {e}")
            messages.pop()
            return
        # 把模型的输出追加到对话历史中
        # append([4,5]) 后: [1, 2, 3, [4, 5]]  ← 整个列表被当成一个元素
        # extend([3,4]) 后: [1, 2, 3, 4]  ← 元素被拆开逐个加入
        msg = response.choices[0].message
        messages.append(msg)

        # 如果 msg.tool_calls 为空列表，说明模型这次没有调用工具，已经给出最终答案，可以直接返回。
        if not msg.tool_calls:
            return msg.content

        # 如果 msg.tool_calls 不为空，就说明模型想调用工具，程序会继续遍历 calls，逐个执行对应函数。

        # 一轮API拿到一批工具任务 本地全部跑完 补齐结果记录再重新找模型
        # 直到模型说不用工具、直接出答案
        # 并行模式 非串行模式
        # 并行：一次模型响应，多个 tool_calls，本地循环跑完所有，再回传
        # 串行：一次模型响应只返回 1 个 tool_call，跑完，再请求模型，模型再给下一个
        for call in msg.tool_calls:
            try:
                # 核心逻辑  json.loads()把 JSON 字符串转换成 Python字典
                # FUNCTIONS[] 根据工具名字符串拿到本地的工具函数
                # **args 字典解包，把参数传给函数调用
                args = json.loads(call.function.arguments)
                # 字典取值用方括号 []
                result = tool_schema.FUNCTIONS[call.function.name](**args)
            except Exception as e:
                result = f"工具错误：{e}"
            # print("调用", call.function.name, call.function.arguments, "=>", result)
            # 只打印调用外部函数 不显示结果
            print("调用", call.function.name)
            #  把工具执行结果以 role="tool" 的标准消息格式写回对话历史
            # 这条消息用来给模型返回工具执行结果，和上面的tool_call配对

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                }
            )
    return "超过最大步骤，已停止"


if __name__ == "__main__":
    chat_counter = 0
    conversation_buffer = []  # 暂存最近20轮对话
    while True:
        user_input = input("用户：").strip()
        conversation_buffer.append(f"{user_input}")
        if not user_input:
            print("输入不能为空，请重新输入")
            continue
        # 结束命令不区分大小写
        if user_input.lower() == "exit":
            print(messages)
            break
        if user_input.lower() == "new":
            # 清空会话：只保留系统指令，去掉历史对话
            # 第一种情况 messagess = [] 时 则

            messages.clear()
            # 第二种情况 需要用到系统指令时 则
            # messagess = [messagess[0]]  # 保留第一条system消息
            print("已开启新对话")
            continue
        agent_result = run_agent(user_input, messages)
        conversation_buffer.append(f"Assistant: {agent_result}")
        print(f"\n模型: {agent_result}")
        chat_counter = chat_counter + 1
        if chat_counter >= 20:
            summary_data = summarize_conversation(conversation_buffer)
            # 自动入库
            save_from_llm(summary_data)
            # 重置
            chat_counter = 0
            conversation_buffer = []
            print()
