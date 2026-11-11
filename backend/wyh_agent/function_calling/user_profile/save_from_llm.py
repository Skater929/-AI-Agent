import json
import backend.wyh_agent.function_calling.user_profile.load_profile as load_profile
import backend.wyh_agent.function_calling.user_profile.save_profile as save_profile
from openai import OpenAI


def save_from_llm(llm_output):
    # 设置JSON的schema强约束
    """
    {
        "basic_info": {
            "name":"",
            "age":"",
            "job:"",
            "preferences":[]
        },
        "long_term_memory": [""]
        "active_tasks_active":[""]
    }
    """

    # isinstance(obj, type) 判断对象类型
    if isinstance(llm_output, str):
        # 如果是字符串，就解析成 dict
        data = json.loads(llm_output)
    else:
        # 如果已经是 dict，直接用
        data = llm_output

    profile = load_profile()  # 调用 load_profile()，读取当前持久化的字典

    # 确保抽屉存在（兼容旧数据或默认结构缺失的情况）
    # dict.setdefault(key, default) 如果 key 存在就返回当前值，不存在则插入 default 并返回
    profile.setdefault("basic_info", {})
    profile.setdefault("long_term_memory", [])
    profile.setdefault("active_tasks_active", [])
    profile["basic_info"].setdefault("preferences", [])  # preferences 初始化为列表

    results = []  # 初始化空列表，用于收集每条操作的提示信息

    for key, value in data.items():  # 遍历字典的所有键值对
        # 语法：dict.items() 返回 (key, value) 元组的可迭代对象；
        # for a, b in ... 是元组解包赋值
        if key == "preferences":
            profile["basic_info"]["preferences"].extend(value)
            results.append("偏好已追加")
        elif key in ["name", "age", "job"]:
            # 常规偏好 -> 存入 basic_info 抽屉
            profile["basic_info"][key] = value
            results.append(f"个人信息已更新")

        elif key == "long_term_memory":
            profile["long_term_memory"].append(value)
            results.append("记忆已追加")

        elif key == "active_tasks_active":
            profile["active_tasks_active"].extend(value)
            results.append("新任务已加入列表")

        # 注意：这里用 elif 而不是 if，避免一个 key 同时命中多个分支

    save_profile(profile)  # 所有字段改完后，一次性写回文件
    return "; ".join(results)  # "; ".join(list) 用分号+空格把列表拼成一个字符串返回
    # 语法：str.join(iterable) 字符串方法
