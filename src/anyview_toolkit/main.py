import threading
import tkinter as tk

import pyautogui

from anyview_toolkit.copy_question import copy_question
from anyview_toolkit.type_answer import type_answer


class AnyviewToolkitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anyview Toolkit")
        self.root.geometry("300x250")

        self.copy_button = tk.Button(
            root,
            text="复制题目(3秒)",
            width=20,
            command=lambda: self.start_countdown(
                self.copy_button, 3, copy_question, "复制题目"
            ),
        )
        self.copy_button.pack(padx=15, pady=15)

        self.type_button = tk.Button(
            root,
            text="输入答案(3秒)",
            width=20,
            command=lambda: self.start_countdown(
                self.type_button, 3, type_answer, "输入答案"
            ),
        )
        self.type_button.pack(padx=15, pady=15)

        # 状态提示标签
        self.status_label = tk.Label(root, text="状态：空闲", fg="blue")
        self.status_label.pack(pady=10)

    def start_countdown(self, btn, remaining, task_func, task_name):
        """处理倒计时逻辑（在主线程中运行）"""

        # 禁用按钮，防止用户在倒计时期间重复点击
        btn.config(state=tk.DISABLED)

        if remaining > 0:
            btn.config(text=f"{task_name} ({remaining}秒)")
            self.status_label.config(text=f"状态：{task_name} 倒计时 {remaining} 秒...")
            # 1000毫秒（1秒）后再次调用自身，实现非阻塞倒计时
            self.root.after(
                1000,
                lambda: self.start_countdown(btn, remaining - 1, task_func, task_name),
            )
        else:
            # 倒计时结束，准备执行功能
            btn.config(text="执行中...")
            self.status_label.config(text=f"状态：正在执行 {task_name}...")
            # 开启新线程执行耗时功能，避免阻塞 GUI 主线程
            threading.Thread(
                target=self.run_task, args=(btn, task_func, task_name), daemon=True
            ).start()

    def run_task(self, btn, task_func, task_name):
        """在子线程中执行实际功能"""
        try:
            task_func()
            # 成功后更新状态
            self.root.after(0, lambda: self.reset_button(btn, task_name, success=True))
        except pyautogui.FailSafeException:
            # 用户触发安全中断
            self.root.after(
                0,
                lambda: self.reset_button(
                    btn,
                    task_name,
                    success=False,
                    msg="⚠️ 已触发安全中断（鼠标移至角落）",
                ),
            )

    def reset_button(self, btn, task_name, success=True, msg=None):
        """恢复按钮和状态（在主线程中运行）"""
        if task_name == "复制题目":
            btn.config(text="复制题目(3秒)", state=tk.NORMAL)
        else:
            btn.config(text="输入答案(3秒)", state=tk.NORMAL)

        if msg:
            self.status_label.config(text=msg, fg="orange" if "⚠️" in msg else "red")
        else:
            self.status_label.config(text="状态：执行完毕！", fg="green")


def main():
    root = tk.Tk()
    app = AnyviewToolkitApp(root)  # noqa: F841
    root.mainloop()


if __name__ == "__main__":
    main()
