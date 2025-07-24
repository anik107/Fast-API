from fastapi import FastAPI
from .models import Base
from .database import engine
from .routers import (
    auth,
    todos,
    users
)
from .routers import admin
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette import status

app = FastAPI()

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="todoApp/templates")
app.mount("/static", StaticFiles(directory="todoApp/static"), name="static")


@app.get("/")
async def root():
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
