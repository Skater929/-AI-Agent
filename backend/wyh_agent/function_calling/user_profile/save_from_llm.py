import json
from backend.wyh_agent.function_calling.user_profile.load_profile import load_profile
from backend.wyh_agent.function_calling.user_profile.save_profile import save_profile


def save_from_llm(basic_info, long_term_memory=None, active_tasks_active=None):
    # 设置JSON的schema强约束
    """
    {
        "basic_info": {
            "name":"",
            "age":"",
            "job":"",
            "preference":[]
        },
        "long_term_memory": [""],
        "active_tasks_active":[""]
    }
    """

    profile = load_profile()  # 调用 load_profile()，读取当前持久化的字典

    # 确保抽屉存在（兼容旧数据或默认结构缺失的情况）
    # dict.setdefault(key, default) 如果 key 存在就返回当前值，不存在则插入 default 并返回
    profile.setdefault("basic_info", {})
    profile.setdefault("long_term_memory", [])
    profile.setdefault("active_tasks_active", [])
    profile["basic_info"].setdefault("preference", [])  # preference 初始化为列表

    results = []  # 初始化空列表，用于收集每条操作的提示信息

    # 处理 basic_info 这个嵌套对象
    # 因为大模型返回的 JSON 中 name/age/job/preference 都在 basic_info 里面
    for key in ["name", "age", "job"]:  # 遍历基本信息的字段
        if key in basic_info:
            # 常规个人信息 -> 存入 basic_info 抽屉
            profile["basic_info"][key] = basic_info[key]
            results.append(f"{key}已更新")

    # 列表 单独处理
    if "preference" in basic_info:
        # list.extend(iterable) 将一个列表的所有元素追加到另一个列表中
        profile["basic_info"]["preference"].extend(basic_info["preference"])
        results.append("偏好已追加")

    # 处理顶层数组字段
    if long_term_memory:
        # 用 extend 而不是 append，避免嵌套列表 [[...]]
        # list.extend(iterable) 将一个列表的所有元素追加到另一个列表中
        profile["long_term_memory"].extend(long_term_memory)
        results.append("记忆已追加")

    if active_tasks_active:
        # list.extend(iterable) 将一个列表的所有元素追加到另一个列表中
        profile["active_tasks_active"].extend(active_tasks_active)
        results.append("新任务已加入列表")

    save_profile(profile)  # 所有字段改完后，一次性写回文件
    return "; ".join(results)  # "; ".join(list) 用分号+空格把列表拼成一个字符串返回
    # 语法：str.join(iterable) 字符串方法
