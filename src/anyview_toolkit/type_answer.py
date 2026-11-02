import random
import string
import time

import pyautogui
import pyperclip

from anyview_toolkit.countdown import countdown

INTRA_GROUP_DELAY = (0.01, 0.02)
INTER_GROUP_DELAY = (0.1, 0.2)
WRONG_CHAR_RATE = 0.05
FIX_CHAR_DELAY = (0.1, 0.2)
MAX_GROUP_LEN = (3, 8)
COUNTDOWN_TIME = 3


_KEYBOARD_ROWS = [
    "`1234567890-=",
    " qwertyuiop[]\\",
    "  asdfghjkl;'",
    "   zxcvbnm,./",
]

_WITHOUT_SHIFT_MAP = {
    "!": "1",
    "@": "2",
    "#": "3",
    "$": "4",
    "%": "5",
    "^": "6",
    "&": "7",
    "*": "8",
    "(": "9",
    ")": "0",
    "_": "-",
    "+": "=",
    "{": "[",
    "}": "]",
    "|": "\\",
    ":": ";",
    '"': "'",
    "<": ",",
    ">": ".",
    "?": "/",
    "~": "`",
}


def _compute_neighbors(keyboard_rows):
    neighbors = {}
    for row, keyboard_row in enumerate(keyboard_rows):
        for col, ch in enumerate(keyboard_row):
            if ch == " ":
                continue
            neighbor = neighbors.setdefault(ch, set())

            # Vertical neighbors (same column, adjacent rows)
            for row_offset in (-1, 1):
                neighbor_row = row + row_offset
                if 0 <= neighbor_row < len(keyboard_rows):
                    adj_row = keyboard_rows[neighbor_row]
                    if col < len(adj_row):
                        adj = adj_row[col]
                        if adj != " ":
                            neighbor.add(adj)

            # Horizontal neighbors (same row, adjacent columns)
            for col_offset in (-1, 1):
                neighbor_col = col + col_offset
                if 0 <= neighbor_col < len(keyboard_row):
                    adj = keyboard_row[neighbor_col]
                    if adj != " ":
                        neighbor.add(adj)

    return neighbors


_KEYBOARD_NEIGHBORS = _compute_neighbors(_KEYBOARD_ROWS)


def random_wrong_char(correct):
    if not correct.isprintable():
        return correct

    candidate = set(_KEYBOARD_NEIGHBORS.get(correct, ()))

    if correct.isupper():
        candidate.add(correct.lower())
    if correct in _WITHOUT_SHIFT_MAP:
        candidate.add(_WITHOUT_SHIFT_MAP[correct])

    candidate.discard(correct)

    if not candidate:
        raise ValueError(f"No wrong-char candidates for {correct!r}")

    return random.choice(tuple(candidate))


def split_into_groups(answer: str) -> list[str]:
    groups = []
    buf = ""
    for ch in answer:
        if ch == " ":
            buf += ch
            groups.append(buf)
            buf = ""
        else:
            buf += ch
            if len(buf) >= MAX_GROUP_LEN[1]:
                cut = random.randint(*MAX_GROUP_LEN)
                groups.append(buf[:cut])
                buf = buf[cut:]
    if buf:
        groups.append(buf)
    # 过滤空组
    return [group for group in groups if group]


def type_error_then_remove(ch, interval: float):
    wrong = random_wrong_char(ch)
    if wrong and wrong != ch:
        pyautogui.write(wrong, interval=interval)
        time.sleep(random.uniform(*FIX_CHAR_DELAY))
        pyautogui.press("backspace")


def type_answer():
    answer = pyperclip.paste()

    countdown(COUNTDOWN_TIME)

    answer = answer.replace("\r\n", "\n").replace("\r", "\n")

    answer = "\n".join(line.lstrip() for line in answer.splitlines())

    pyautogui.press("tab")

    groups = split_into_groups(answer)
    for group in groups:
        for ch in group:
            interval = random.uniform(*INTRA_GROUP_DELAY)
            if ch == " ":
                pyautogui.write(ch, interval=interval)
            elif ch == "\n":
                pyautogui.press("enter")
            elif ch == "}":
                pyautogui.press("down")
            else:
                if random.random() < WRONG_CHAR_RATE:
                    type_error_then_remove(ch, interval=interval)
                pyautogui.write(ch, interval=interval)

        time.sleep(random.uniform(*INTER_GROUP_DELAY))
