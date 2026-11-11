# 1. 导入必要的库
import json              # json 模块：处理 JSON 数据，dumps 序列化（对象→字符串），loads 反序列化（字符串→对象）
from pathlib import Path # Path 类：面向对象的路径操作，比字符串路径更安全、跨平台

# 2. 定义全局常量：数据文件路径
FILE = Path("data/tasks.json")
# Path("data/tasks.json") 创建一个路径对象，指向当前目录下的 data/tasks.json 文件

# 3. 加载任务：从 JSON 文件读取任务列表
def load_tasks():
    if not FILE.exists():          # .exists() 检查文件是否存在，不存在说明是首次运行
        return []                  # 返回空列表，避免后续操作报错
    try:
        # .read_text(encoding="utf-8") 读取文件全部文本，utf-8 保证中文不乱码
        # json.loads(...) 将 JSON 字符串解析为 Python 列表（内含字典）
        return json.loads(FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:   # 捕获 JSON 格式错误（文件被手动改坏时不会崩溃）
        return []                  # 解析失败也返回空列表，程序继续运行

# 4. 保存任务：将任务列表写入 JSON 文件
def save_tasks(tasks):
    # tasks 参数：接收一个列表（元素为任务字典），这是要保存的数据

    FILE.parent.mkdir(exist_ok=True)
    # .parent 获取文件的父目录（即 data 文件夹）
    # .mkdir(exist_ok=True) 创建目录，exist_ok=True 表示目录已存在时不报错

    
    FILE.write_text(
        json.dumps(tasks, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    # json.dumps 参数说明：
    #   tasks            — 要序列化的 Python 对象
    #   ensure_ascii=False — 中文直接输出，不转成 \uXXXX
    #   indent=2         — 缩进 2 空格，生成的 JSON 文件美观易读



# 5. 添加任务
def add_task(title):
    # title 参数：字符串，新任务的标题
    tasks = load_tasks()   # 先读取已有任务，避免覆盖之前的数据
    tasks.append({
        "id": len(tasks) + 1,   # 用当前列表长度+1 作为新 ID（简单自增）
        "title": title,          # 任务标题
        "done": False            # 初始状态为未完成
    })
    save_tasks(tasks)            # 追加后立即持久化到文件


# 6. 标记任务完成
def complete_task(task_id):
    # task_id 参数：整数，要标记完成的任务 ID
    tasks = load_tasks()


    
    for task in tasks:           # 遍历任务列表，逐个比对
        if task["id"] == task_id: # 找到匹配 ID
            task["done"] = True   # 修改状态为已完成（字典是可变对象，直接改即可）
            save_tasks(tasks)     # 保存回文件
            return True           # 找到并修改成功，返回 True
    return False                 # 遍历完都没找到，返回 False（错误 ID 不崩溃）


# 7. 列出所有未完成的任务
def list_pending():
    tasks = load_tasks()
    # 列表推导式：筛选出 done 为 False 的任务，返回新列表
    return [t for t in tasks if not t["done"]]


# 第一轮测试：此时文件为空，id=1 不存在
complete_task(1)       # 返回 False，静默处理，不报错
complete_task(999)     # 返回 False，同样不崩溃
print("未完成：", list_pending())  # 输出 []，因为还没有任何任务

# 第二轮：添加任务后再操作
add_task("完成 Python 第一章")
print("所有任务：", load_tasks())   # 输出包含 1 条任务的列表


complete_task(1)       # id=1 已存在，成功标记为完成，返回 True
complete_task(999)     # 错误 ID，返回 False，程序正常运行
print("未完成：", list_pending())  # 输出 []，因为唯一任务已完成