Implemented an employee management web app through FastAPI and an employee's task management CLI through Typer. SQLAlchemy was used to work with a SQLite database, and Alembic was used for DB migration.

Each employee has an associated department and a list of tasks.

### Pre-requisites:

- Create new Poetry project: `poetry new emgmt` or initialize inside an existing folder: `poetry init`
- Activate the virtual environment: `Invoke-Expression (poetry env activate)`
- add dependencies with: `poetry add fastapi[standard] sqlalchemy typer alembic`

### Launching the WebApp

- `fastapi dev .\src\emgmt\app.py`
- Once the above command has been run, CRUD methods can be tested out [here](http://127.0.0.1:8000/docs).

The web app can be used to perform CRUD operations on the `employee` table and the `department` table.

### The CLI Interface

- The CLI program can be run with: `poetry run python -m src.emgmt.cli.tasks --help` This will also list the available commands.
- More information about these commands can be viewed using `python -m src.emgmt.cli.tasks <command-name> --help`

The CLI can be used to perform CRUD operations on the `task` table.

### DB Schema Migration

```
alembic upgrade head
alembic revision --autogenerate -m "message"
```

### To Do

- add authorization logic
- schedule tasks with FastAPI