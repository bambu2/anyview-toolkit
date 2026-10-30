import sys
from pathlib import Path


def load_text(file_name: str) -> str:
    """从 txt 文件读取文本"""
    path = Path(__file__).resolve().parent / file_name
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"文件不存在：{path}")
        sys.exit(1)
    except OSError as e:
        print(f"读取文件失败：{e}")
        sys.exit(1)

    if not text.strip():
        print("文件内容为空，退出。")
        sys.exit(1)

    return text
