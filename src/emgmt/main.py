from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from httpx import AsyncClient

# from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
import uvicorn

from src.emgmt.database import get_db
from src.emgmt.models import Employee
from src.emgmt.routers import departments, employees, auth, upload_files
from src.emgmt.utils import create_admin_user  # , get_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.client = AsyncClient()
    await create_admin_user()
    yield
    await app.client.aclose()


app = FastAPI(title="Employee Management Web Portal", lifespan=lifespan)


# app.mount(
#     "/static", StaticFiles(directory="src/emgmt/templates"), name="static"
# )


templates = Jinja2Templates(directory="src/emgmt/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, session: Session = Depends(get_db)):
    context = {
        "request": request,
        "employees": session.execute(select(Employee)).scalars().all(),
    }
    return templates.TemplateResponse("index.html", context)


# @app.get("/external")
# async def external(client: AsyncClient = Depends(get_client)):
#     external_api_url = "https://jsonplaceholder.typicode.com/users"
#     response = await client.get(external_api_url)
#     users = response.json()
#     return users


@app.get("/external")
async def external(request: Request):
    external_api_url = "https://jsonplaceholder.typicode.com/users"
    client = request.app.client
    response = await client.get(external_api_url)
    users = response.json()
    return users


app.include_router(auth.router)
app.include_router(departments.router)
app.include_router(employees.router)
app.include_router(upload_files.router)


if __name__ == "__main__":
    uvicorn.run("src.emgmt.main:app", host="127.0.0.1", port=8000, reload=True)
