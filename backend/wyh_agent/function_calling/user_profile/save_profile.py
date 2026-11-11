import json
from pathlib import Path

FILE = Path("profile.json")


def save_profile(profile):  # 定义函数，接收一个 dict 参数
    FILE.write_text(json.dumps(profile, ensure_ascii=False, indent=2), "utf-8")
    # json.dumps(...) 把 dict 序列化成 JSON 字符串
    #   ensure_ascii=False 允许写入中文等非 ASCII 字符（否则会被转成 \uXXXX）
    #   indent=2 格式化缩进，便于人读
