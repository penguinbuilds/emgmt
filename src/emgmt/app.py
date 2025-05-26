from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.emgmt.database import create_db_and_tables
from src.emgmt.routers import employees
from src.emgmt.routers import departments


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(employees.router)
app.include_router(departments.router)


# def main():
#     pass


# if __name__ == "__main__":
#     main()
