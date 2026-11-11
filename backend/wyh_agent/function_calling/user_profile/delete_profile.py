import backend.wyh_agent.function_calling.user_profile.load_profile as load_profile
import backend.wyh_agent.function_calling.user_profile.save_profile as save_profile
import json


def delete_profile(llm_response):
    # 设置返回的schama必须为匹配当前外部函数的格式
    # {"tasks_active": ["要删除的任务名"], "long_term_memory": ["要删除的记忆内容"]}
    """
    从配置文件中删除指定的任务。
    支持模糊匹配，即只要输入的任务名与现有任务存在包含关系，就会被视为匹配成功。
    """

    try:
        data = json.loads(llm_response)
    except json.JSONDecodeError:
        return "JSON解析失败，请检查大模型返回格式"
    data1 = data.get("active_tasks_active", [])
    data2 = data.get("long_term_memory", [])
    # 1. 从文件中加载当前的配置信息（profile）
    profile = load_profile()

    # 2. 获取文件中的任务列表，如果没有则默认为空列表
    tasks_active = profile.get("active_tasks_active", [])
    long_term_memories = profile.get("long_term_memory", [])

    # 3. 初始化一个列表，用于记录每次删除操作的结果（成功或失败）
    results = []

    # 4. 遍历需要删除的长期记忆
    for tasks in data1:
        # 如果传入的任务名为空字符串或None，则跳过本次循环，避免无意义的匹配
        if not tasks:
            continue

        # 【核心逻辑：模糊匹配】
        # 使用列表推导式，遍历现有的 tasks_active 列表
        # 匹配条件：如果传入的 task 包含在现有任务 t 中，或者现有任务 t 包含在传入的 task 中
        # 例如：传入 "task1"，现有任务为 "task1_backup"，两者存在包含关系，就会被匹配到
        matched = [t for t in tasks_active if tasks in t or t in tasks]

        # 5. 如果找到了匹配的任务
        if matched:
            # 从本地tasks_active 列表中移除第一个匹配到的任务（避免重复删除）
            tasks_active.remove(matched[0])

            # 记录删除成功的提示信息
            results.append(f"已删除任务：{matched[0]}")
        else:
            # 6. 如果没有找到任何匹配的任务，记录未找到的提示信息
            results.append(f"未找到：{tasks}")

    # 4. 遍历需要删除的任务列表
    for memories in data2:
        # 如果传入的任务名为空字符串或None，则跳过本次循环，避免无意义的匹配
        if not memories:
            continue

        # 【核心逻辑：模糊匹配】
        # 使用列表推导式，遍历现有的 tasks_active 列表
        # 匹配条件：如果传入的 task 包含在现有任务 t 中，或者现有任务 t 包含在传入的 task 中
        # 例如：传入 "task1"，现有任务为 "task1_backup"，两者存在包含关系，就会被匹配到
        matched = [m for m in long_term_memories if memories in m or m in memories]
        # 5. 如果找到了匹配的任务
        if matched:
            # 从long_term_memories 列表中移除第一个匹配到的任务（避免重复删除）
            long_term_memories.remove(matched[0])
            # 记录删除成功的提示信息
            results.append(f"已删除记忆：{matched[0]}")
        else:
            # 6. 如果没有找到任何匹配的任务，记录未找到的提示信息
            results.append(f"未找到：{memories}")

    # 7. 循环结束后，将更新后的任务列表写回 profile 字典中
    profile["active_tasks_active"] = tasks_active
    profile["long_term_memory"] = long_term_memories
    # 8. 统一保存一次配置文件（避免在循环内频繁读写文件，提升性能）
    save_profile(profile)

    # 9. 将所有结果通过换行符拼接成一个完整的字符串并返回
    return "\n".join(results)
