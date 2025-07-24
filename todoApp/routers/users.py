from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, status
from ..database import SessionLocal
from ..models import Users
from .auth import get_current_user
from passlib.context import CryptContext


router = APIRouter(
    prefix="/user",
    tags=["user"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependencies = Annotated[Session, Depends(get_db)]
user_dependencies = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)
    model_config = {
        "json_schema_extra": {
            "example": {
                "password": "old_password",
                "new_password": "new_password"
            }
        }
    }
@router.get("/", status_code=status.HTTP_200_OK)
async def read_user(user: user_dependencies, db: db_dependencies):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return db.query(Users).filter(Users.id == user.get("id")).first()

@router.put("/password", status_code=status.HTTP_200_OK)
async def update_password(user: user_dependencies,
                           db: db_dependencies,
                           user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_user = db.query(Users).filter(Users.id == user.get("id")).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not bcrypt_context.verify(user_verification.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    db_user.hashed_password = bcrypt_context.hash(user_verification.new_password)

    db.add(db_user)
    db.commit()
    return {"message": "Password updated successfully"}

@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependencies,
                           db: db_dependencies,
                           phone_number: str = Path(min_length=10, max_length=15)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_user = db.query(Users).filter(Users.id == user.get("id")).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.phone_number = phone_number
    db.add(db_user)
    db.commit()
    return {"message": "Phone number updated successfully"}
