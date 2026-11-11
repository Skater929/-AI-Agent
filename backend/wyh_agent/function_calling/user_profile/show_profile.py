import backend.wyh_agent.function_calling.user_profile.load_profile as load_profile
import json


def show_profile():
    profile = load_profile()
    # json.dumps 把 dict 序列化成带缩进的 JSON 字符串，便于人眼阅读
    print(json.dumps(profile, ensure_ascii=False, indent=4))
