from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, status
from ..models import Users, TodoItem
from ..database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependencies = Annotated[Session, Depends(get_db)]
user_dependencies = Annotated[dict, Depends(get_current_user)]

@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependencies, db: db_dependencies):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    todos = db.query(TodoItem).filter(TodoItem.owner_id == user.get("id")).all()
    if not todos:
        raise HTTPException(status_code=404, detail="No todos found")
    return todos

@router.delete("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def delete_todo(user: user_dependencies, db: db_dependencies, todo_id: int = Path(gt=0)):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id)\
        .filter(TodoItem.owner_id == user.get('id')).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}