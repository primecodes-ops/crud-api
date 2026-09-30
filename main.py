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


class taskChange(BaseModel):
    title: str
    done: bool


class taskOut(BaseModel):
    id: int
    title: str
    done: bool


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
async def get_tasks(done: bool | None = None, search: str | None = None):
    result = task_objects

    if done is not None:
        result = [task for task in result if task["done"] == done]

    if search is not None:
        result = [task for task in result if search.lower() in task["title"].lower()]

    return result


"""
curl -i [http://localhose:8000/tasks]
"""


@app.get("/tasks/{id}")
async def get_task(id: int):
    task = next((item for item in task_objects if item["id"] == id), None)

    if task is None:
        return JSONResponse(status_code=404, content={"error": "Task 99 not found"})

    return task


"""
curl -i [http://localhose:8000/tasks/{id}]
"""


@app.post("/tasks", status_code=201, response_model=taskOut)
async def create(task: taskCreate):
    if not task.title or not task.title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is empty"})

    id = max((t["id"] for t in task_objects), default=0) + 1
    task_objects.append({"id": id, "title": task.title, "done": False})

    return {"id": id, "title": task.title, "done": False}


"""
curl -i -X POST [http://localhost:8000/tasks] -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
"""


@app.put("/tasks/{id}", response_model=taskOut)
async def update(id: int, task: taskChange):
    if not task.title or not task.title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is empty"})

    for item in task_objects:
        if item["id"] == id:
            item["title"] = task.title
            item["done"] = task.done
            return item

    return JSONResponse(status_code=404, content={"error": "Task not found."})


"""
curl -i -X PUT [http://localhost:8000/tasks/{id}] -H "Content-Type: application/json" -d '{"title":"Buy bread", "done": false}'
"""


@app.delete("/tasks/{id}", status_code=204)
async def delete(id: int):
    for i, item in enumerate(task_objects):
        if item["id"] == id:
            task_objects.pop(i)
            return

    return JSONResponse(status_code=404, content={"error": "Task not found."})


"""
curl -i -X DELETE [http://localhost:8000/tasks/{id}]
"""
