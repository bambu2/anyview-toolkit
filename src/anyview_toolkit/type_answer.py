import random
import string
import time

import pyautogui
import pyperclip
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn

INTRA_GROUP_DELAY = (0.01, 0.02)
INTER_GROUP_DELAY = (0.1, 0.2)
WRONG_CHAR_RATE = 0.05
FIX_CHAR_DELAY = (0.1, 0.2)
SKIP_SPACE_RATE = 0.8  # 移除“符号左右两侧空格”的概率（成对删除；其他空格不删）
MAX_GROUP_LEN = (3, 8)  # 超长无空白串随机切块长度范围
COUNTDOWN_TIME = 1.5


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

_FINGER_GROUPS = [
    set("qaz1"),
    set("wsx2"),
    set("edc3"),
    set("rfv4"),
    set("tgb5"),
    set("yhn6"),
    set("ujm7"),
    set("ik,8"),
    set("ol.9"),
    set("p;/0"),
]


def _build_neighbors():
    neighbors = {}
    rows = _KEYBOARD_ROWS
    height = len(rows)

    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == " ":
                continue

            # setdefault -> robust if the same key appears more than once
            nb = neighbors.setdefault(ch, set())

            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue

                    nr, nc = r + dr, c + dc
                    if not (0 <= nr < height):
                        continue

                    adj_row = rows[nr]
                    if not (0 <= nc < len(adj_row)):
                        continue

                    adj = adj_row[nc]
                    if adj != " " and adj != ch:
                        nb.add(adj)

    return neighbors


_NEIGHBORS = _build_neighbors()


def _finger_typo(ch):
    low = ch.lower()
    for group in _FINGER_GROUPS:
        if low in group:
            candidate = [key for key in group if key != low]
            if candidate:
                c = random.choice(candidate)
                return c.upper() if ch.isupper() else c
    return None


def random_wrong_char(correct):
    if not correct.isprintable():
        return correct

    rand = random.random()

    if rand < 0.60:
        nb = _NEIGHBORS.get(correct)
        return random.choice(tuple(nb)) if nb else correct
    elif rand < 0.75:
        if correct.isalpha():
            return correct.lower()
    elif rand < 0.90:
        if correct in _WITHOUT_SHIFT_MAP:
            return _WITHOUT_SHIFT_MAP[correct]
    else:
        f = _finger_typo(correct)
        if f and f != correct:
            return f

    # 兜底：没有合适的错误字符，就“不打错”
    return correct


def remove_specific_space(text: str) -> str:
    """
    只有符号两边都有空格才按 SKIP_SPACE_RATE 概率两侧一起删.
    """
    n = len(text)
    out = []
    i = 0
    while i < n:
        ch = text[i]

        # 非空格：原样输出
        if ch != " ":
            out.append(ch)
            i += 1
            continue

        # 连续空格段 [i, j)
        j = i
        while j < n and text[j] == " ":
            j += 1

        # 是否为 "空格段 + 符号 + 空格段" 模式
        if j < n and text[j] in string.punctuation and j + 1 < n and text[j + 1] == " ":
            k = j + 1
            while k < n and text[k] == " ":
                k += 1

            if random.random() < SKIP_SPACE_RATE:
                # 成对删除两侧空格，只留符号
                out.append(text[j])
            else:
                # 成对保留
                out.extend(text[i:j])
                out.append(text[j])
                out.extend(text[j + 1 : k])
            i = k
            continue

        # 普通空格（含符号只有单边空格的情况）：全部保留
        out.extend(text[i:j])
        i = j

    return "".join(out)


def split_into_groups(text):
    groups = []
    buf = ""
    for ch in text:
        if ch == " ":
            buf += ch
            groups.append(buf)
            buf = ""
        else:
            buf += ch
            if len(buf) >= MAX_GROUP_LEN[1]:
                # 到达上限，随机切一刀
                cut = random.randint(*MAX_GROUP_LEN)
                groups.append(buf[:cut])
                buf = buf[cut:]
    if buf:
        groups.append(buf)
    # 过滤空组
    return [group for group in groups if group]


def type_char(ch):
    if ch == "\n":
        pyautogui.press("enter")
    elif ch == "\t":
        pyautogui.press("tab")
    elif ch.isprintable():
        pyautogui.write(ch)
    else:
        # 非 ASCII 跳过
        pass


def type_with_errors(ch):
    if random.random() < WRONG_CHAR_RATE:
        wrong = random_wrong_char(ch)
        if wrong and wrong != ch:
            type_char(wrong)
            time.sleep(random.uniform(*INTRA_GROUP_DELAY))
            time.sleep(random.uniform(*FIX_CHAR_DELAY))
            pyautogui.press("backspace")
            time.sleep(random.uniform(*INTRA_GROUP_DELAY))
    type_char(ch)


def countdown(t: float) -> None:
    steps = 100
    interval = t / steps  # 每次 tick 的真实耗时，总时长 = t 秒

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeRemainingColumn(compact=True),
    ) as progress:
        task = progress.add_task(
            description="请把焦点切到目标文本框！",
            total=steps,
        )
        for _ in range(steps):
            time.sleep(interval)
            progress.advance(task, 1)  # 也可写 progress.update(task, advance=1)


def type_answer():
    text = pyperclip.paste()

    countdown(COUNTDOWN_TIME)
    print("开始")

    text = remove_specific_space(text)
    groups = split_into_groups(text)
    for group in groups:
        for ch in group:
            if ch == " ":
                type_char(ch)
                time.sleep(random.uniform(*INTRA_GROUP_DELAY))
                continue
            type_with_errors(ch)
            time.sleep(random.uniform(*INTRA_GROUP_DELAY))
