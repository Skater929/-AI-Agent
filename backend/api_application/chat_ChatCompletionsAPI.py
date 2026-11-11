import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()

# 创造client前检测key 避免调用API才报错
api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    # 手动抛出（触发）异常，中断正常流程
    raise EnvironmentError("未设置 DEEPSEEK_API_KEY 环境变量")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

# 用列表维护对话历史，每条消息是一个字典
# 初始放入系统指令

# 不需要设定 AI 人设 可以为空 可以直接从空列表开始：
# messages = []

# 需要设定AI人设 则需要指定 例如
# messages = [
#     {
#         "role": "system",  # 系统级指令 所以类别为系统 这条消息不会显示在对话中 但存储在messages中
#         "content": "你是一位严格的代码审查员。请指出用户代码中的问题，包括性能、可读性、安全性等方面，并给出改进建议。不要直接重写代码，而是引导用户自己修改。",
#     }
# ]

messages = []

while True:

    question = input("用户：").strip()

    if not question:
        print("输入不能为空，请重新输入")
        continue

    # 结束命令不区分大小写
    if question.lower() == "exit":
        break

    if question.lower() == "new":
        # 清空会话：只保留系统指令，去掉历史对话
        # 第一种情况 messages = [] 时 则
        messages.clear()

        # 第二种情况 需要用到系统指令时 则
        # messages = [messages[0]]  # 保留第一条system消息
        print("已开启新对话")
        continue

    # 把用户消息加入历史记录
    messages.append({"role": "user", "content": question})
    try:
        # 调用 DeepSeek Chat Completions API
        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=messages,
            stream=False,
            # reasoning_effort参数在关闭思考模式disabled的时候需要去掉
            # reasoning_effort="low",
            extra_body={"thinking": {"type": "disabled"}},
        )
    except openai.AuthenticationError:
        # 捕获认证错误 (401)
        print("\n[致命错误] API Key 无效或已过期，请检查 .env 配置并重启程序。")
        messages.pop()
        break  # 直接退出循环，不浪费算力重试

    except openai.RateLimitError:
        # 捕获限流错误 (429)
        print("\n[限流警告] 请求过于频繁，程序将自动暂停 10 秒后重试...")
        messages.pop()  # 移除未发送成功的用户消息
        time.sleep(10)  # 暂停 10 秒
        continue  # 跳过后续代码，直接开始下一次 while 循环重试

    except openai.APIConnectionError as e:
        # 捕获网络连接错误
        print(f"\n[网络错误] 无法连接到服务器: {e}")
        print("请检查你的网络连接或防火墙设置。")
        messages.pop()
        continue

    except openai.APIStatusError as e:
        # 捕获服务器错误 (如 500, 503 等)
        print(f"\n[服务器错误] DeepSeek 服务异常: {e}")
        print("服务器正忙，请稍后重新提问。")
        messages.pop()
        continue

    except Exception as e:
        # 兜底：捕获其他所有未预料的错误
        print(f"\n[未知异常] 发生未定义的错误: {e}")
        messages.pop()
        continue

    # 获取AI回复
    # n的值是回复的个数 n=3 就会返回 3 个候选回复
    ai_reply = response.choices[0].message.content

    # 把AI回复也加入历史记录，实现上下文连贯
    messages.append({"role": "assistant", "content": ai_reply})

    # 打印回复
    print("AI：", ai_reply)
