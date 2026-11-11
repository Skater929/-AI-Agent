import json
from pathlib import Path

#定义路径常量
FILE=Path("data/tasks.json")

#从json文件中读取任务
def load_tasks():
    if not FILE.exists():
        return []
    try:
        return json.loads(FILE.read_text(encoding="utf-8"))

    except json.JSONDecodeError:
        return []


#追加任务
def add_tasks(title):
    tasks=load_tasks()

    #读取的JSON文件格式为列表和字典 这里用append
    tasks.append({
        "id":len(tasks)+1,
        "title":title,
        "done":False
    })

    # 写入到文件当中
    save_tasks(tasks)


# 保存任务
def save_tasks(tasks):
    # 接收新的JSON
    FILE.parent.mkdir(exist_ok=True)
    # exist_ok=True 目录如果存在 无影响
    FILE.write_text(json.dumps(tasks,ensure_ascii=False,indent=2),encoding="utf-8")


# 更新任务状态
def tasks_updata(task_id):
    tasks=load_tasks()
    for task in tasks:
        if task["id"]==task_id:
            task["done"]=True
            break
    else:
        return '任务不存在'
    
     #循环里改完它就已经变了，最后统一保存一次就行。
    save_tasks(tasks)
    return "修改完成"


# #列出未完成任务
# def no_tasks():
#     tasks = load_tasks()
#     return [t for t in tasks if not t["done"]]  # 返回所有未完成任务的列表


# # 测试

# #读取（加载）任务
# all_tasks=load_tasks()
# for i in all_tasks:
#     print(f" [{i['id']}] {i['title']}")


# print("------------------")


# # 获取未完成任务
# pending=no_tasks()
# for t in pending:
#     print(f" [{t['id']}] {t['title']}")


# # 追加任务
# add_tasks("测试1")

# # 更新任务状态
# status=tasks_updata(11)
# print(status)