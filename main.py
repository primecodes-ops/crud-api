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


"""
curl -i [http://localhose:port/tasks]
"""


@app.get("/tasks/{id}")
async def task(id: int):
    task = next((item for item in task_objects if item["id"] == id), None)

    if task is None:
        return JSONResponse(status_code=404, content={"error": "Task 99 not found"})

    return task


"""
curl -i [http://localhose:port/tasks/{id}]
"""


@app.post("/tasks/", status_code=201, response_model=taskCreate)
async def create(task: taskCreate):
    if not task.title or not task.title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is empty"})

    id = task_objects[-1]["id"] + 1
    task_objects.append({"id": id, "title": task, "done": False})

    return {"id": id, "title": task, "done": False}


"""
curl -i -X POST [http://localhost:port/tasks] -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
"""


@app.put("/tasks/{id}", response_model=taskChange)
async def update(id: int, task: taskChange):
    if not task.title or not task.title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is empty"})

    if not isinstance(task.done, bool):
        return JSONResponse(
            status_code=400, content={"error": "Done can only be true or false."}
        )

    for item in task_objects:
        if item["id"] == id:
            item["title"] = task.title
            item["done"] = task.done
            return item

    return JSONResponse(status_code=404, content={"error": "Task not found."})


"""
curl -i -X PUT [http://localhost:port/tasks/{id}] -H "Content-Type: application/json" -d '{"title":"Buy bread", "done": false}'
"""


@app.delete("/tasks/{id}", status_code=204)
async def delete(id: int):
    for i, item in enumerate(task_objects):
        if item["id"] == id:
            task_objects.pop(i)
            return

    return JSONResponse(status_code=404, content={"error": "Task not found."})


"""
curl -i -X DELETE [http://localhost:port/tasks/{id}]
"""
