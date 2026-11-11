# 导入 OpenAI 客户端类 用于调用大模型
from openai import OpenAI

# 通过os库 把环境变量的密钥拿出来
import os

# 导入加载环境变量的函数 拿密钥
from dotenv import load_dotenv

# 自动读取项目根目录下的 .env 文件，将里面的配置（如 API Key）加载到系统环境变量中
load_dotenv()

# 初始化 OpenAI 客户端，它会自动从环境变量中读取 OPENAI_API_KEY 进行认证
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1"
)

# 初始化变量，用于保存上一轮对话的响应ID，以实现多轮对话的上下文记忆
previous_id = None

# 开启一个无限循环，实现持续的多轮对话
while True:
    # 获取用户输入，strip() 用于去除首尾多余的空格或换行符
    question = input("用户：").strip()

    # 如果用户输入 "exit"，则退出循环，结束程序
    if question == "exit":
        break

    if question == "new":
        # 清空上一轮的响应ID 断开上下文 开启新对话
        previous_id = None
        continue

    # 构建发送给大模型的请求参数字典
    args = {
        "model": "",  # 指定使用的模型名称
        # 设置系统级长期指令（System Prompt）定义AI的角色和行为规范
        # 如果需要 每轮（次）对话都需要设置该参数
        "instructions": "",
        "input": question,  # 传入用户当前这一轮的提问内容
    }

    # 如果存在上一轮的响应ID，则将其加入请求参数中
    # 这样模型就能根据之前的对话历史来回答，实现上下文连贯
    # 第一轮时 previous_id 是 None，条件不成立，直接跳过
    # 从第二轮开始，previous_id 已经有值了，就把它塞进请求参数里，告诉服务端"请基于上一轮继续"
    if previous_id:
        # 向args加入该键值对
        args["previous_response_id"] = previous_id

        # args = {
        #     "model": "...",
        #      "instructions": "...",
        #     "input": question,
        #     "previous_response_id": previous_id,  # 新增这一项
        #     }

    # 调用 Responses API 创建对话响应
    # 这里参数内用 ** 自动解包
    # 不管字典里有几个键都能正确传参
    # 因为previous_id有时有 有时没有
    response = client.responses.create(**args)

    # 将当前响应的 ID 保存下来，供下一轮对话使用
    # 这行删掉会强制每次都是全新对话（不要上下文）
    previous_id = response.id

    # 打印AI回复的文本内容
    print("AI：", response.output_text)
