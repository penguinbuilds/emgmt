from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse

# from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
import uvicorn

from src.emgmt.database import get_db
from src.emgmt.models import Employee
from src.emgmt.routers import departments, employees, login


app = FastAPI(title="Employee Management Web Portal")

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


app.include_router(login.router)
app.include_router(departments.router)
app.include_router(employees.router)


if __name__ == "__main__":
    uvicorn.run("src.emgmt.main:app", host="127.0.0.1", port=8000, reload=True)
