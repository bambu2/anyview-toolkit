import re

from anyview_toolkit.load_text import load_text


# TODO:paperclip
def clean_question(path="question.txt", encoding="utf-8"):
    # 1. 读取
    content = load_text(path)

    # 2. 删除所有 <> 内的内容（含尖括号）
    content = re.sub(r"<[^>]*>", "", content, flags=re.DOTALL)

    # 3. 合并成一行：把换行、连续空白都压成单个空格，再 strip
    content = re.sub(r"\s+", " ", content).strip()

    # 4. 写回原文件
    with open(path, "w", encoding=encoding) as f:
        f.write(content)


if __name__ == "__main__":
    clean_question("question.txt")  # 改成你的文件路径
