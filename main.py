from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()

task_objects = [
    {"id": 1, "title": "Finish CRUD API", "done": False},
    {"id": 5, "title": "Feed cats' lunch", "done": True},
]


class taskCreate(BaseModel):
    title: str


@app.get("/")
async def root():
    return {"message": "hello world"}


@app.get("/api")
async def describe_api():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/tasks")
async def tasks():
    return task_objects


@app.get("/tasks/{id}")
async def task(id: int):
    task = next((item for item in task_objects if item["id"] == id), None)

    if task is None:
        return JSONResponse(status_code=404, content={"error": "Task 99 not found"})

    return task


@app.post("/tasks/", status_code=201)
async def create(task: taskCreate):
    if not task.title or not task.title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is empty"})

    id = task_objects[-1]["id"] + 1
    task_objects.append({"id": id, "title": task, "done": False})

    return {"id": id, "title": task, "done": False}
