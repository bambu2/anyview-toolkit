import re

import pyperclip


def copy_question():
    text = pyperclip.paste()
    
    text = text.split("】", 1)[-1]
    
    text = re.sub(r"<[^>]*>", "", text, flags=re.DOTALL)

    text = re.sub(r"\s+", " ", text).strip()

    pyperclip.copy(text)
