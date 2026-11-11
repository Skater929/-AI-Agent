# 1. 定义变量，模拟 Agent 的基本配置状态
name = "学习 Agent"  # 字符串(str)：定义 Agent 的名称
week = 1  # 整数(int)：定义当前的学习周数
finished = False  # 布尔值(bool)：定义学习状态是否完成

# 2. 定义核心对话数据结构（字典组成的列表）
messages = [
 {"role": "system", "content": "你是一名老师"}, # 列表第0个元素是字典(dict)：系统指令(System Prompt)，用于设定 AI 的角色和基调
 {"role": "user", "content": "什么是 Agent？"},  # 列表第1个元素是字典(dict)：用户的提问内容
]




# 3. 使用 for 循环遍历消息列表
for message in messages:
 # 循环体：每次循环，'message' 变量都会依次接收列表中的一个字典


 #for 负责把一个个字典拆出来赋值给 message，然后 message["role"] 负责在拆出来的字典里精准抓取你想要的 role 标签


 # 通过 message["role"] 获取角色标签，message["content"] 获取对话内容，并用 print 格式化打印出来
 print(message["role"], "=>", message["content"])




 def estimate_level(hours: int) -> str:
    if hours < 10: return "入门"
    if hours < 50: return "进阶"
    return "可以做项目"

for hours in [3, 20, 80]:
    print(hours, estimate_level(hours))