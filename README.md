Implemented an employee management web app with FastAPI, and an employee's task management CLI with Typer. SQLAlchemy was used for ORM, and Alembic was used for DB migration. The PostgresSQL database and the FastAPI app are both running on Docker containers.

Each employee has an associated department and a list of tasks.

### Pre-requisites:

- Create new Poetry project: `poetry new emgmt` or initialize inside an existing folder: `poetry init`
- Activate the virtual environment: `Invoke-Expression (poetry env activate)` or `python -m venv .venv`
- install dependencies with: `poetry install` or `pip install -r requirements.txt`
- create a `.env` file based on `.env.local`

### Launching the Application

- `docker build . -t fastapi-app`
- `docker-compose up --build`
- Once the above commands have been run, CRUD methods can be tested out [here](http://127.0.0.1:8000/docs).

The web app can be used to perform CRUD operations on the `employee` table and the `department` table.

### The CLI Interface

- The CLI program can be run from within the Docker container using: `-m src.emgmt.cli.tasks --help` This will also list the available commands.
- More information about these commands can be viewed using `python -m src.emgmt.cli.tasks <command-name> --help`

The CLI can be used to perform CRUD operations on the `task` table.

### DB Schema Migration

```
alembic upgrade head
alembic revision --autogenerate -m "message"
```

### Authentication & Role Based Access

When the application starts up for the first time, an admin is also initialized. Only the admin can perform CRUD operations on the `employee` and `department` tables.

The `Display Departments` GET method and `Display Employees` GET method do not require signing in, and they show limited details.

The `Get Department` GET method will only return department details if accessed by the admin or an employee that belongs to that department.

The `Get Employee` GET method method will only return employee details if accessed by the admin or the employee themself.

### Cert Generation

`openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx.key -out nginx.crt -subj "//CN=localhost"`