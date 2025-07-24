import logging
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, status, Request
from starlette.responses import RedirectResponse
from models import TodoItem
from database import SessionLocal
from routers.auth import get_current_user
from fastapi.templating import Jinja2Templates
from pathlib import Path

_logger = logging.getLogger(__name__)

# Get the absolute path to the templates directory
templates = Jinja2Templates(directory="todoApp/templates")

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependencies = Annotated[Session, Depends(get_db)]
user_dependencies = Annotated[dict, Depends(get_current_user)]

class TodoItemRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(ge=1, le=5)
    completed: bool = Field(default=False)

    model_config = {
        "json_schema_extra":{
            "example": {
                "title": "Buy groceries",
                "description": "Milk, Bread, Eggs",
                "priority": 2,
                "completed": False
            }
        }
    }


def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie("access_token")
    return redirect_response

### Pages ###

@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependencies):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        todos = db.query(TodoItem).filter(TodoItem.owner_id == user.get("id")).all()
        todo_list = []
        for todo in todos:
            todo_list.append({
                "id": todo.id,
                "title": todo.title,
                "description": todo.description,
                "priority": todo.priority,
                "completed": todo.completed
            })
        return templates.TemplateResponse("todo.html", {"request": request, "todos": todo_list, "user": user})
    except Exception as e:
        _logger.error(f"Error in render_todo_page: {str(e)}")
        return redirect_to_login()

@router.get("/add-todo-page")
async def render_add_todo_page(request: Request, db: db_dependencies):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})
    except Exception as e:
        _logger.error(f"Error in render_add_todo_page: {str(e)}")
        return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependencies):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        todo = db.query(TodoItem).filter(TodoItem.id == todo_id)\
            .filter(TodoItem.owner_id == user.get('id')).first()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})
    except Exception as e:
        _logger.error(f"Error in render_edit_todo_page: {str(e)}")
        return redirect_to_login()

### Endpoints ###
@router.get("/")
async def read_all(user: user_dependencies, db: db_dependencies):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return db.query(TodoItem).filter(TodoItem.owner_id == user.get("id")).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependencies,db: db_dependencies, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id)\
        .filter(TodoItem.owner_id == user.get('id')).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependencies,
                      db: db_dependencies,
                      todo: TodoItemRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    new_todo = TodoItem(**todo.model_dump(), owner_id=user.get("id"))
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependencies,
                    db: db_dependencies,
                    todo_request: TodoItemRequest,
                    todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    todo_model = db.query(TodoItem).filter(TodoItem.id == todo_id)\
        .filter(TodoItem.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.completed = todo_request.completed

    db.add(todo_model)
    db.commit()
    return None

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependencies,
        db: db_dependencies,
        todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    todo_model = db.query(TodoItem).filter(TodoItem.id == todo_id)\
        .filter(TodoItem.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo_model)
    db.commit()
    return None