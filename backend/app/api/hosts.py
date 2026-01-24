from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..db import get_db
from ..models import Host, AuthType

router = APIRouter(prefix="/hosts", tags=["hosts"])

class HostBase(BaseModel):
    name: str
    ip: str
    ssh_port: int = 22
    username: str
    auth_type: AuthType = AuthType.password
    password: Optional[str] = None
    tags: Optional[List[str]] = []

class HostCreate(HostBase):
    pass

class HostRead(HostBase):
    id: int
    
    class Config:
        from_attributes = True

@router.post("/", response_model=HostRead)
def create_host(host: HostCreate, db: Session = Depends(get_db)):
    db_host = Host(
        name=host.name,
        ip=host.ip,
        ssh_port=host.ssh_port,
        username=host.username,
        auth_type=host.auth_type,
        password=host.password,
        tags=host.tags
    )
    db.add(db_host)
    db.commit()
    db.refresh(db_host)
    return db_host

@router.get("/", response_model=List[HostRead])
def get_hosts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    hosts = db.query(Host).offset(skip).limit(limit).all()
    return hosts

@router.put("/{host_id}", response_model=HostRead)
def update_host(host_id: int, host: HostCreate, db: Session = Depends(get_db)):
    db_host = db.query(Host).filter(Host.id == host_id).first()
    if db_host is None:
        raise HTTPException(status_code=404, detail="Host not found")
    
    for key, value in host.dict().items():
        setattr(db_host, key, value)
    
    db.commit()
    db.refresh(db_host)
    return db_host

@router.delete("/{host_id}")
def delete_host(host_id: int, db: Session = Depends(get_db)):
    db_host = db.query(Host).filter(Host.id == host_id).first()
    if db_host is None:
        raise HTTPException(status_code=404, detail="Host not found")
    
    db.delete(db_host)
    db.commit()
    return {"ok": True}
