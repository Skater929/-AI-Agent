from pathlib import Path
import json

FILE = Path("profile.json")


def load_profile():
    FILE.parent.mkdir(parents=True, exist_ok=True)
    # mkdir(parents=True, exist_ok=True) 创建目录，已存在也不报错；parents=True 会递归创建所有缺失的父目录
    # 语法：关键字参数 exist_ok=True, parents=True
    if not FILE.exists():
        return {"basic_info": {}, "long_term_memory": [], "active_tasks_active": []}
        # 返回默认结构，避免后续 profile["basic_info"][key] 报 KeyError

    try:
        return json.loads(FILE.read_text("utf-8"))
        # FILE.read_text("utf-8") 用 UTF-8 编码读取文件全部内容，返回 str
        # json.loads(s) 把 JSON 字符串解析成 Python 对象（这里是 dict）
    except json.JSONDecodeError:
        return {"basic_info": {}, "long_term_memory": [], "active_tasks_active": []}
        # 文件损坏时返回默认结构，防止程序崩溃
