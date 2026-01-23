from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from ..db import get_db
from ..models import User
from ..auth import get_current_admin_user, get_password_hash

router = APIRouter(prefix="/users", tags=["users"])

class UserBase(BaseModel):
    username: str
    is_active: bool = True
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[UserRead])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    return db.query(User).all()

@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        is_active=1 if user.is_active else 0,
        is_admin=1 if user.is_admin else 0
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    # current_user: User = Depends(get_current_admin_user)
    # if user_id == current_user.id:
    #    raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db.delete(user)
    db.commit()
    return {"msg": "User deleted"}
