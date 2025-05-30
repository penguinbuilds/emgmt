# from typing_extensions import Annotated
# from uuid import UUID

# from sqlalchemy import select
# from sqlalchemy.orm import Session
# import typer

# from src.emgmt.database import engine
# from src.emgmt.models import Department, Employee, Task
# from src.emgmt.utils import save_result_to_json

# app = typer.Typer()

# MODEL_MAP = {"department": Department, "employee": Employee, "task": Task}


# @app.command
# def convert_to_json(
#     tablename: Annotated[
#         str,
#         typer.Argument(help="Name of the table which must be ported to JSON."),
#     ],
#     # entity: Annotated[
#     #     UUID | int,
#     #     typer.Option(help="ID of the entity that must be ported to JSON."),
#     # ],
# ) -> None:
#     model = MODEL_MAP.get(tablename.lower())

#     if not model:
#         typer.echo(f"Table: {tablename}")
#         raise typer.Exit(code=1)

#     with Session(engine) as session:
#         result = session.execute(select(tablename))
#         save_result_to_json(result, tablename)


# if __name__ == "__main__":
#     app()
