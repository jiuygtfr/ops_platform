from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from ..db import get_db
from ..models import EnvConfig, EnvConfigType

router = APIRouter(prefix="/env-configs", tags=["env-configs"])

class EnvConfigBase(BaseModel):
    name: str
    type: EnvConfigType
    content: str

class EnvConfigCreate(EnvConfigBase):
    pass

class EnvConfigUpdate(EnvConfigBase):
    pass

class EnvConfigOut(EnvConfigBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[EnvConfigOut])
def get_env_configs(type: EnvConfigType = None, db: Session = Depends(get_db)):
    query = db.query(EnvConfig)
    if type:
        query = query.filter(EnvConfig.type == type)
    return query.all()

@router.post("/", response_model=EnvConfigOut)
def create_env_config(config: EnvConfigCreate, db: Session = Depends(get_db)):
    db_config = EnvConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.put("/{config_id}", response_model=EnvConfigOut)
def update_env_config(config_id: int, config: EnvConfigUpdate, db: Session = Depends(get_db)):
    db_config = db.query(EnvConfig).filter(EnvConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    for key, value in config.dict().items():
        setattr(db_config, key, value)
    
    db.commit()
    db.refresh(db_config)
    return db_config

@router.delete("/{config_id}")
def delete_env_config(config_id: int, db: Session = Depends(get_db)):
    db_config = db.query(EnvConfig).filter(EnvConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    db.delete(db_config)
    db.commit()
    return {"ok": True}
