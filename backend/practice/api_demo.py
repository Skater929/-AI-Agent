# 导入所需库
import httpx  # 现代 HTTP 客户端，比 requests 更简洁，原生支持异步
import os  # 操作系统接口，这里用来读取环境变量
from dotenv import load_dotenv  # 从 .env 文件加载键值对到环境变量中


def github_user(name):

    # 调用 GitHub API 查询指定用户的基本信息。
    # 参数: name (str): GitHub 用户名
    # 返回:dict: 成功时返回用户信息字典（含 login, id, avatar_url 等字段）；
    #  失败时返回 {"error": 错误描述}
    try:
        # 发送 GET 请求，timeout=10 表示最多等待 10 秒，避免程序卡死
        r = httpx.get(f"https://api.github.com/users/{name}", timeout=10, verify=False)

        # 检查响应状态码：如果是 4xx 或 5xx，自动抛出 HTTPStatusError
        r.raise_for_status()

        # 将 JSON 响应体解析为 Python 字典并返回
        return r.json()

    except httpx.HTTPStatusError as e:
        # HTTP 层面的错误：请求发出了，但服务器返回了错误状态码
        # 常见情况：404 用户不存在、403 频率限制、401 未授权
        return {"error": f"状态码 {e.response.status_code}"}

    except httpx.RequestError as e:
        # 网络层面的错误：请求根本没发出去或中途失败
        # 常见情况：超时、DNS 解析失败、网络连接断开
        return {"error": f"网络失败：{e}"}


# 测试：查询 openai 组织的公开信息
print(github_user("Skater929"))


# 以下代码再需要密钥的情况下在使用 本例无需密钥
# # load_dotenv() 会查找当前工作目录下的 .env 文件，
# # 将其中的 KEY=VALUE 行注入到 os.environ 中，之后才能用 os.getenv 读取
# load_dotenv()

# # 从环境变量中取出密钥；如果 .env 里没写或者文件名不对，这里会拿到 None
# key = os.getenv("OPENAI_API_KEY")

# # 防御性检查：密钥为空时立刻中断，避免后续调用 API 时才报错、难以排查
# if not key:
#     raise RuntimeError("没有找到密钥，请检查项目根目录下是否有 .env 文件并正确填写 OPENAI_API_KEY")
