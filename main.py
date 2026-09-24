from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

task_objects = [
    {"id": 1, "title": "Finish CRUD API", "done": False},
    {"id": 5, "title": "Feed cats' lunch", "done": True},
]


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
