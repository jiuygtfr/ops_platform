from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .db import Base
import enum
import datetime

class AuthType(str, enum.Enum):
    password = "password"
    private_key = "private_key"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Integer, default=1) # 1: active, 0: inactive
    is_admin = Column(Integer, default=0)  # 1: admin, 0: regular

class Host(Base):
    __tablename__ = "hosts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    ip = Column(String(64))
    ssh_port = Column(Integer, default=22)
    username = Column(String(64))
    auth_type = Column(Enum(AuthType), default=AuthType.password)
    password = Column(String(255), nullable=True)
    private_key_id = Column(Integer, nullable=True)
    tags = Column(JSON, nullable=True)

class TaskMode(str, enum.Enum):
    single = "single"
    broadcast = "broadcast"
    batch = "batch"

class BatchFailStrategy(str, enum.Enum):
    continue_ = "continue"
    pause_on_fail = "pause_on_fail"

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    command = Column(Text)
    mode = Column(Enum(TaskMode), default=TaskMode.broadcast)
    batch_size = Column(Integer, nullable=True)
    batch_interval = Column(Integer, nullable=True)
    on_batch_fail_strategy = Column(Enum(BatchFailStrategy), nullable=True)
    creator_id = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    task_hosts = relationship("TaskHost", back_populates="task")

class TaskHostStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"

class TaskHost(Base):
    __tablename__ = "task_hosts"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    host_id = Column(Integer, ForeignKey("hosts.id"))
    status = Column(Enum(TaskHostStatus), default=TaskHostStatus.pending)
    exit_code = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    
    task = relationship("Task", back_populates="task_hosts")

class EnvConfigType(str, enum.Enum):
    account = "account"
    topology = "topology"

class EnvConfig(Base):
    __tablename__ = "env_configs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    type = Column(Enum(EnvConfigType))
    content = Column(Text) # YAML content
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
