from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, users, boards, columns, tasks, demand_types

app = FastAPI(title="TaskFlow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(boards.router, prefix="/api/boards", tags=["boards"])
app.include_router(columns.router, prefix="/api/columns", tags=["columns"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(demand_types.router, prefix="/api/demand-types", tags=["demand_types"])

@app.get("/")
def root():
    return {"message": "TaskFlow API está rodando!"}
