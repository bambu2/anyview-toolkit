def load_text(path: str) -> str:
    """从 txt 文件读取文本"""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    return text
