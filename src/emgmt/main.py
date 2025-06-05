from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, Request, Depends, BackgroundTasks, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse

# from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import Session
import uvicorn

from src.emgmt.celery import create_task
from src.emgmt.database import get_db
from src.emgmt.models import Employee
from src.emgmt.routers import departments, employees, auth, upload_files
from src.emgmt.utils import (
    create_admin_user,
    html,
    write_notification,
)  # , get_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.client = AsyncClient()
    await create_admin_user()
    yield
    await app.client.aclose()


app = FastAPI(
    title="Employee Management Web Portal", version="v1", lifespan=lifespan
)


# app.mount(
#     "/static", StaticFiles(directory="src/emgmt/templates"), name="static"
# )


templates = Jinja2Templates(directory="src/emgmt/templates")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, session: Session = Depends(get_db)):
    context = {
        "request": request,
        "employees": session.execute(select(Employee)).scalars().all(),
    }
    return templates.TemplateResponse("index.html", context)


@app.get("/chat/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.post("/celery-task")
async def celery_task(delay: int, x: int, y: int):
    task = create_task.delay(delay, x, y)
    return JSONResponse({"Task:": task.get()})


@app.get("/get_headers")
async def get_all_request_headers(request: Request):
    headers = request.headers
    selected_headers = {
        "User-Agent": headers.get("user-agent"),
        "Accept-Encoding": headers.get("accept-encoding"),
        "Referer": headers.get("referer"),
        "Accept-Language": headers.get("accept-language"),
        "Connection": headers.get("connection"),
        "Host": headers.get("host"),
    }
    return selected_headers


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


@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some message")
    return {"message": "notification sent in background."}


app.include_router(auth.router)
app.include_router(departments.router)
app.include_router(employees.router)
app.include_router(upload_files.router)


if __name__ == "__main__":
    uvicorn.run("src.emgmt.main:app", host="127.0.0.1", port=8000, reload=True)
