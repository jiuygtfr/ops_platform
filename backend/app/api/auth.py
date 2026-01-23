from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..auth import verify_password, create_access_token, get_password_hash
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    is_admin: bool

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "username": user.username,
        "is_admin": bool(user.is_admin)
    }

# Init default admin user (helper endpoint, remove or protect in prod)
@router.post("/init-admin")
def init_admin(db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == "admin").first():
        return {"msg": "Admin already exists"}
    
    admin_user = User(
        username="admin",
        hashed_password=get_password_hash("admin"),
        is_active=1,
        is_admin=1
    )
    db.add(admin_user)
    db.commit()
    return {"msg": "Admin created (admin/admin)"}
