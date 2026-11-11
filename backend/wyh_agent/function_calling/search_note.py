NOTES_PATH = "./data/note.txt"


def search_note(KEYWORD):
    match_lines = []
    try:
        with open(NOTES_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if KEYWORD.lower() in line.lower():
                    match_lines.append(line)
                    if len(match_lines) >= 5:
                        break
    except FileNotFoundError:
        return "文件不存在！"
    except Exception as e:
        return f"读取失败！原因：{str(e)}"

    if not match_lines:
        return f"文件中没有找到关键词{KEYWORD}的内容"

    # 底层："第一行内容\n第二行内容\n第三行内容"
    return "\n".join(match_lines)
