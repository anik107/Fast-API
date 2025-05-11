from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, status
from ..models import Users, TodoItem
from ..database import SessionLocal
from .auth import get_current_user

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