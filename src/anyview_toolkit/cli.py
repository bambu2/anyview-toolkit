import typer

from anyview_toolkit.copy_question import copy_question
from anyview_toolkit.type_answer import type_answer

app = typer.Typer()


@app.command()
def copy():
    copy_question()


@app.command()
def type():
    type_answer()


if __name__ == "__main__":
    app()
