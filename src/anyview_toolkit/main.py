import threading
import tkinter as tk

import pyautogui

from anyview_toolkit.copy_question import copy_question
from anyview_toolkit.type_answer import type_answer


class AnyviewToolkitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anyview Toolkit")
        self.root.geometry("480x360")

        self.cancel_after_id = None
        self.is_counting = False

        self._idle_after_id = None

        self.copy_button = tk.Button(
            root,
            text="复制题目",
            width=20,
            command=lambda: self.start_countdown(
                self.copy_button, 3, copy_question, "复制题目"
            ),
        )
        self.copy_button.pack(padx=15, pady=10)

        self.type_button = tk.Button(
            root,
            text="输入答案",
            width=20,
            command=lambda: self.start_countdown(
                self.type_button, 3, type_answer, "输入答案"
            ),
        )
        self.type_button.pack(padx=15, pady=10)

        # --- 新增：停止倒计时按钮 ---
        self.stop_button = tk.Button(
            root,
            text="停止倒计时",
            width=20,
            fg="red",
            command=self.stop_countdown,
        )
        self.stop_button.pack(padx=15, pady=10)

        # 状态提示标签
        self.status_label = tk.Label(root, text="状态：空闲", fg="blue")
        self.status_label.pack(pady=10)

    def start_countdown(self, btn, remaining: int, task_func, task_name: str):
        """处理倒计时逻辑（在主线程中运行）"""

        # 禁用功能按钮，防止重复点击
        btn.config(state=tk.DISABLED)
        self.is_counting = True

        if remaining > 0 and self.is_counting:
            self.status_label.config(
                text=f"⏱ {remaining} 秒后执行 {task_name}", fg="blue"
            )
            # 保存 after ID，以便后续取消
            self.cancel_after_id = self.root.after(
                1000,
                lambda: self.start_countdown(btn, remaining - 1, task_func, task_name),
            )
        elif self.is_counting:
            # 倒计时正常结束，清除标记并执行任务
            self.is_counting = False
            self.cancel_after_id = None

            btn.config(text="执行中...")
            self.status_label.config(text=f"状态：正在执行 {task_name}...", fg="blue")

            threading.Thread(
                target=self.run_task, args=(btn, task_func), daemon=True
            ).start()

    def stop_countdown(self):
        """取消当前正在进行的倒计时"""
        if self.cancel_after_id is not None:
            self.root.after_cancel(self.cancel_after_id)
            self.cancel_after_id = None

        if self.is_counting:
            self.is_counting = False
            # 恢复所有功能按钮为可用状态
            self.copy_button.config(state=tk.NORMAL)
            self.type_button.config(state=tk.NORMAL)
            self.status_label.config(text="❌倒计时已取消", fg="orange")

    def run_task(self, btn, task_func):
        try:
            task_func()
            self.root.after(0, lambda: self.reset_button(btn))
        except pyautogui.FailSafeException:
            self.root.after(
                0,
                lambda: self.reset_button(btn, "⚠️已触发安全中断（鼠标移至屏幕角落）"),
            )

    def reset_button(self, btn, msg: str | None = None):
        btn.config(state=tk.NORMAL)

        if btn == self.copy_button:
            btn.config(text="复制题目")
        elif btn == self.type_button:
            btn.config(text="输入答案")

        if msg:
            self.status_label.config(text=msg, fg="orange" if "⚠️" in msg else "red")
        else:
            self.status_label.config(text="✅执行完毕！", fg="green")

        # 1 秒后自动还原为“状态：空闲”
        if hasattr(self, "_idle_after_id") and self._idle_after_id is not None:
            self.root.after_cancel(self._idle_after_id)
        self._idle_after_id = self.root.after(
            1000, lambda: self.status_label.config(text="状态：空闲", fg="blue")
        )


def main():
    root = tk.Tk()
    app = AnyviewToolkitApp(root)  # noqa: F841
    root.mainloop()


if __name__ == "__main__":
    main()
