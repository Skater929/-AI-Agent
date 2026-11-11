from backend.wyh_agent.function_calling.calculator import calculator
from backend.wyh_agent.function_calling.current_time import current_time
from backend.wyh_agent.function_calling.search_note import search_note
from backend.wyh_agent.function_calling.get_weather import get_weather

# 工具函数集合
FUNCTIONS = {
    "calculator": calculator,
    "current_time": current_time,
    "search_note": search_note,
    "get_weather": get_weather,
}

# 工具描述列表，告诉模型"有哪些工具可用、每个工具需要什么参数"
# Function Calling / Tool Use 的核心

# `name` 必须和你 `FUNCTIONS` 字典的 key 一模一样，大小写敏感
# `strict=True` + `additionalProperties:False` 是强约束，模型参数错了就会调用失败
# `description` 是给模型看的，不是给代码看的，写得差会导致模型不调用 / 乱调用
TOOLS = [
    # 第一个工具：计算器
    {
        # type：工具类型，固定写function，表示这是一个函数调用工具
        "type": "function",
        "function": {
            # name：工具名称，模型调用时会返回这个名字，用来和本地FUNCTIONS字典匹配
            "name": "calculator",
            # strict：开启严格schema校验，强制模型严格遵守参数规则，不能乱生成参数
            # 模型生成的参数 JSON必须严格遵守自己写的schema
            # 不允许额外字段（和下面 `additionalProperties:False` 配合）
            "strict": True,
            # description：给模型看的文字描述，模型依靠这段文字判断什么时候调用这个工具
            "description": "精确计算",
            # parameters：参数规则，使用JSON Schema规范，告诉模型需要生成什么样的参数
            "parameters": {
                # type：参数整体是一个对象（对应Python字典）
                "type": "object",
                # properties：定义每一个参数的名称、类型、约束
                "properties": {
                    # 根据parameters schema 调用工具时会返回符合该字段规范的 JSON 字符串
                    # 例如{"a": 100, "b": 20, "operation": "divide"}
                    # a参数，类型是number，支持整数、浮点数
                    "a": {"type": "number"},
                    # b参数，类型是number，支持整数、浮点数
                    "b": {"type": "number"},
                    # operation参数，字符串类型，并且只能取enum里面指定的值
                    "operation": {
                        "type": "string",
                        # enum = 枚举，约束：模型生成的参数 适合固定选项
                        # 只能三选一：add / multiply / divide
                        # 不允许出现不在列表里的值
                        "enum": ["add", "multiply", "divide"],
                    },
                },
                # required：必填参数列表，strict开启后，模型必须返回这三个参数，不能缺少
                "required": ["a", "b", "operation"],
                # additionalProperties:False，禁止模型自己额外增加schema里没有定义的参数
                "additionalProperties": False,
            },
        },
    },
    # 第二个工具：获取当前时间
    {
        "type": "function",
        "function": {
            "name": "current_time",
            "strict": True,
            "description": "获取当前时间",
            "parameters": {
                "type": "object",
                # properties为空，代表这个工具不需要传入任何参数
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    # 增加只读本地文件的外部工具
    {
        "type": "function",
        "function": {
            "name": "search_note",
            "strict": True,
            "description": "在本地固定笔记文件中搜索关键词，查找相关笔记内容，最多返回5条匹配行；仅用于查询笔记",
            "parameters": {
                "type": "object",
                "properties": {
                    "KEYWORD": {"type": "string", "description": "要查询的关键词"}
                },
                "required": ["KEYWORD"],
                "additionalProperties": False,
            },
        },
    },
    # 获取天气情况工具
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "strict": True,
            "description": "获取当前某个城市的天气、气温、体感温度的信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city_name": {"type": "string", "description": "需要查询的城市名"}
                },
                "required": ["city_name"],
                "additionalProperties": False,
            },
        },
    },
]
