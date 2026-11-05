import re

import pyautogui
import pyperclip

from anyview_toolkit.countdown import countdown

COUNTDOWN_TIME = 3


def copy_question():
    question = pyperclip.paste()

    question = question.split("】", 1)[-1]

    question = re.sub(r"<[^>]*>", "", question, flags=re.DOTALL)

    question = re.sub(r"\s+", " ", question).strip()

    copy_code(question)


def first_blank_line(s: str) -> int | None:
    for i, line in enumerate(s.split("\n")):
        if not line.strip():  # empty or whitespace-only
            return i  # 0-indexed
    return None  # no blank line found


def copy_code(question: str):
    countdown(COUNTDOWN_TIME)

    pyautogui.hotkey("ctrl", "a")

    pyautogui.hotkey("ctrl", "c")

    code = pyperclip.paste()

    blank_line_index = first_blank_line(code)

    pyautogui.press("up")

    if blank_line_index is not None:
        for _ in range(3):
            pyautogui.press("down")

    full_question = f"{question}\n{code}"

    pyperclip.copy(full_question)
