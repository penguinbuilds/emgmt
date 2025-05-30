# from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

# from src.emgmt.database import create_db_and_tables
from src.emgmt.routers import employees
from src.emgmt.routers import departments


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     create_db_and_tables()
#     yield


# app = FastAPI(lifespan=lifespan)

app = FastAPI(title="Employee Management Web Portal")

app.include_router(employees.router)
app.include_router(departments.router)


if __name__ == "__main__":
    uvicorn.run("src.emgmt.main:app", host="127.0.0.1", port=8000, reload=True)
