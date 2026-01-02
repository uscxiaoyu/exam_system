from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.routers import config, upload, grade, history, settings
from backend.api.v1.endpoints import auth, classes, students, sections, tasks, async_tasks

app = FastAPI(title="Smart Grading System Pro API")

# CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(classes.router, prefix="/api/v1/classes", tags=["classes"])
app.include_router(students.router, prefix="/api/v1/students", tags=["students"])
app.include_router(sections.router, prefix="/api/v1", tags=["sections"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(async_tasks.router, prefix="/api/v1", tags=["async"])
app.include_router(config.router)
app.include_router(upload.router)
app.include_router(grade.router)
app.include_router(history.router)
app.include_router(settings.router)

@app.get("/")
def read_root():
    return {"message": "Smart Grading System Pro API is running"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
