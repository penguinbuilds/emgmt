from typing_extensions import Annotated

from sqlalchemy import select
from sqlalchemy.orm import Session
import typer

from src.emgmt.database import engine
from src.emgmt.models import Employee, Task

app = typer.Typer()


@app.command()
def add_task(
    username: Annotated[
        str,
        typer.Argument(
            help="Username of the employee to whom the task must be assigned."
        ),
    ],
    title: Annotated[
        str,
        typer.Option(
            default=...,
            help="Enter title of the task.",
            prompt="Enter task title",
        ),
    ],
    description: Annotated[
        str,
        typer.Option(
            default=" ",
            help="Description for task.",
            prompt="Enter task description",
        ),
    ],
    task_status: Annotated[
        str,
        typer.Option(
            help="Completion status of task.",
            prompt="Has this task been completed? (y/n)",
        ),
    ],
) -> None:
    with Session(engine) as session:
        employee = session.execute(
            select(Employee).where(Employee.username == username)
        ).scalar_one_or_none()
        if employee:
            completed: bool = False
            if task_status == "y":
                completed = True
            task = Task(
                title=title,
                description=description,
                completed=completed,
                employee_id=employee.id,
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            typer.echo("Task added.")
            return
        else:
            typer.echo("Invalid username. Exiting...")
            raise typer.Exit(code=1)


@app.command()
def update_task(
    username: Annotated[
        str,
        typer.Argument(
            help="Username of the employee to whom the task must be assigned."
        ),
    ],
    task_id: Annotated[
        str,
        typer.Option(
            default=...,
            help="Enter task id of the task.",
            prompt="Enter task id",
        ),
    ],
    description: Annotated[
        str,
        typer.Option(
            help="Description for task.",
            prompt="Enter task description",
        ),
    ],
    task_status: Annotated[
        str,
        typer.Option(
            help="Completion state of task.",
            prompt="Has this task been completed? (y/n)",
        ),
    ],
) -> None:
    with Session(engine) as session:
        employee = session.execute(
            select(Employee).where(Employee.username == username)
        ).scalar_one_or_none()
        if employee:
            task = session.execute(
                select(Task).where(Task.id == task_id)
            ).scalar_one_or_none()
            if task:
                completed: bool = False
                if task_status == "y":
                    completed = True
                task.description = description
                task.completed = completed
                session.add(task)
                session.commit()
                typer.echo("Task updated.")
                return
            else:
                typer.echo("Invalid task id. Exiting...")
                raise typer.Exit(code=1)
        else:
            typer.echo("Invalid username. Exiting...")
            raise typer.Exit(code=1)


@app.command()
def delete_task(
    username: Annotated[
        str,
        typer.Argument(
            help="Username of the employee whose task must be deleted."
        ),
    ],
    task_id: Annotated[
        str,
        typer.Option(
            default=...,
            help="Enter task id of the task.",
            prompt="Enter task id",
        ),
    ],
) -> None:
    with Session(engine) as session:
        employee = session.execute(
            select(Employee).where(Employee.username == username)
        ).scalar_one_or_none()
        if employee:
            task = session.execute(
                select(Task).where(Task.id == task_id)
            ).scalar_one_or_none()
            if task:
                session.delete(task)
                session.commit()
                typer.echo("Task deleted.")
                return
            else:
                typer.echo("Invalid task id. Exiting...")
                raise typer.Exit(code=1)
        else:
            typer.echo("Invalid username. Exiting...")
            raise typer.Exit(code=1)


@app.command()
def view_tasks(
    username: Annotated[
        str,
        typer.Argument(
            help="Username of the employee whose tasks you wanna view."
        ),
    ],
) -> None:
    with Session(engine) as session:
        employee = session.execute(
            select(Employee).where(Employee.username == username)
        ).scalar_one_or_none()
        if employee:
            tasks = (
                session.execute(
                    select(Task)
                    .join(Employee)
                    .where(Employee.username == username)
                )
                .scalars()
                .all()
            )
            for task in tasks:
                completed: str = "No"
                if task.completed:
                    completed = "Yes"
                typer.echo(
                    f"\nTask ID: {task.id}\nTitle: {task.title}\nDescription: {task.description}\nTask Completed: {completed}\n"
                )
            return
        else:
            typer.echo("Invalid username. Exiting...")
            raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
