import time

from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn


def countdown(t: float) -> None:
    steps = 10
    interval = t / steps

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
            progress.advance(task, 1)
