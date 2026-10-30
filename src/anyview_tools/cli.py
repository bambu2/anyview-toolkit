import random
import string
import time

from load_text import load_text

try:
    import pyautogui
except ImportError:
    raise SystemExit("请先安装: uv pip install pyautogui")


# ---------------- 可调参数 ----------------
INTRA_DELAY = (0.01, 0.02)  # 组内字符间隔（秒）——快速
INTER_DELAY = (0.1, 0.2)  # 组间停顿（秒）——慢
ERROR_RATE = 0.05  # 每个字符打错概率
ERROR_PAUSE = (0.1, 0.2)  # 打错后停顿再删
SKIP_WS_RATE = 0.8  # 移除“符号左右两侧空格”的概率（成对删除；其他空格不删）
MAX_GROUP_LEN = (3, 8)  # 超长无空白串随机切块长度范围
FOCUS_WAIT = 1.5
# ------------------------------------------


# ---------- 键盘邻近 / 错误字符 ----------
_KEYBOARD_ROWS = [
    "`1234567890-=",
    " qwertyuiop[]\\",
    "  asdfghjkl;'",
    "   zxcvbnm,./",
]
_SHIFT_MAP = {  # 漏按 Shift：理想 -> 实际
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
    nb_all = {}
    for r, row in enumerate(_KEYBOARD_ROWS):
        for c, ch in enumerate(row):
            if ch == " ":
                continue
            nb = set()
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < len(_KEYBOARD_ROWS):
                        row2 = _KEYBOARD_ROWS[nr]
                        if 0 <= nc < len(row2) and row2[nc] != " ":
                            nb.add(row2[nc])
            if ch.isalpha():
                nb.add(ch.swapcase())
            nb_all[ch] = nb
            if ch.isalpha():
                nb_all[ch.lower()] = nb
                nb_all[ch.upper()] = nb
    return nb_all


_NEIGHBORS = _build_neighbors()


def _finger_typo(ch):
    low = ch.lower()
    for group in _FINGER_GROUPS:
        if low in group:
            cand = [key for key in group if key != low]
            if cand:
                c = random.choice(cand)
                return c.upper() if ch.isupper() else c
    return None


def random_wrong_char(correct):
    if not correct.isprintable():
        return correct

    rand = random.random()

    if rand < 0.60:
        nb = _NEIGHBORS.get(correct)
        if nb:
            c = random.choice(tuple(nb))
            if c != correct:
                return c
    elif rand < 0.75:
        if correct.isalpha():
            return correct.lower()
    elif rand < 0.90:
        if correct in _SHIFT_MAP:
            return _SHIFT_MAP[correct]
        if correct.isdigit():
            c = random.choice(string.digits)
            if c != correct:
                return c
    else:
        f = _finger_typo(correct)
        if f and f != correct:
            return f

    # 兜底：没有合适的错误字符，就“不打错”
    return correct


def is_symbol(ch: str) -> bool:
    """判断是否为标点/符号：可打印、非字母数字、非空白。
    中文字符 isalnum() 为 True，不会被当成符号；
    ，。！？ 等全角标点会被当成符号。"""
    return ch.isprintable() and not ch.isalnum() and not ch.isspace()


def apply_space_policy(text: str) -> str:
    """
    在打字之前先把空格去留决定好：
      - 只有“符号两边都有空格”的模式（如 " , " / " 。 " / "  ,  "），
        才按 SKIP_WS_RATE 概率成对删除（两侧一起删）；
        否则成对保留。
      - 其他位置的普通空格一律保留。
      - 制表符/换行等非空格空白原样保留。
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
        if j < n and is_symbol(text[j]) and j + 1 < n and text[j + 1] == " ":
            k = j + 1
            while k < n and text[k] == " ":
                k += 1

            if random.random() < SKIP_WS_RATE:
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
    """
    把文本切成"打字组"：
      - 以空格/制表符/回车作为自然组边界（空白归到前一组末尾）
      - 超长无空白串按随机长度再切块
    返回 list[str]，每个元素是一组要连续快速输入的字符
    """
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
    return [g for g in groups if g]


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
    if random.random() < ERROR_RATE:
        wrong = random_wrong_char(ch)
        if wrong and wrong != ch:
            type_char(wrong)
            time.sleep(random.uniform(*INTRA_DELAY))
            time.sleep(random.uniform(*ERROR_PAUSE))
            pyautogui.press("backspace")
            time.sleep(random.uniform(*INTRA_DELAY))
    type_char(ch)


def countdown(seconds: float, decimals: int = 1, refresh: float = 0.02):
    if seconds <= 0:
        print("⏰ 时间到!")
        return

    end = time.monotonic() + seconds
    fmt = f"\r倒计时: {{:.{decimals}f}}s   "  # 尾部空格清掉残留字符

    while True:
        left = end - time.monotonic()
        if left <= 0:
            break
        print(fmt.format(left), end="", flush=True)
        time.sleep(min(refresh, left))  # 临近结束别睡过头

    print(fmt.format(0.0))  # 归零后换行


def main():
    text = load_text("answer.txt")

    print(f"\n请把焦点切到目标文本框，{FOCUS_WAIT} 秒后开始……")
    countdown(FOCUS_WAIT)
    print("开始")

    text = apply_space_policy(text)  # ← 先统一决定空格去留
    groups = split_into_groups(text)
    for gi, group in enumerate(groups):
        for ch in group:
            if ch == " ":
                type_char(ch)
                time.sleep(random.uniform(*INTRA_DELAY))
                continue
            type_with_errors(ch)
            time.sleep(random.uniform(*INTRA_DELAY))
        if gi < len(groups) - 1:
            time.sleep(random.uniform(*INTER_DELAY))
        # 组间停顿（最后一组不停）
        if gi < len(groups) - 1:
            time.sleep(random.uniform(*INTER_DELAY))

    print("完成")


if __name__ == "__main__":
    main()
