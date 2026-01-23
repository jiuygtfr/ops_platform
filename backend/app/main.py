from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import engine, Base
from .api import hosts, terminal, tasks, auth, users

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ops Platform API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In prod, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(hosts.router)
app.include_router(terminal.router)
app.include_router(tasks.router)

@app.get("/")
def read_root():
    return {"message": "Ops Platform API is running"}
