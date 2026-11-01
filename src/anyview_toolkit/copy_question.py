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


def copy_code(question: str):
    countdown(COUNTDOWN_TIME)

    pyautogui.hotkey("ctrl", "a")

    pyautogui.hotkey("ctrl", "c")

    pyautogui.press("up")
    for _ in range(3):
        pyautogui.press("down")

    code = pyperclip.paste()

    full_question = f"{question}\n{code}"

    pyperclip.copy(full_question)
