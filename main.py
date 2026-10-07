from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from contextlib import closing
import sqlite3

# Initializing FastAPI()
app = FastAPI()


# Creating task BaseModel
class taskCreate(BaseModel):
    title: str


# Displaying task BaseModel
class taskOut(BaseModel):
    title: str
    done: int


# Updating task BaseModel
class taskChange(BaseModel):
    title: str
    done: int


# Insert task function
def insert_task(db, data):
    try:
        with closing(sqlite3.connect(db)) as conn:
            cursor = conn.cursor()

            # Insert tasks
            cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", data)
            conn.commit()

    except sqlite3.OperationalError as e:
        print(f"Error 500: Database error: {e}")
        raise HTTPException(status_code=500, detail={"error": "Database error"})


# Path to the SQLite database file (created automatically if missing)
db = "tasks.db"


# Create tasks table
create_table_query = """CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY,
                        title TEXT,
                        done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0,1))
                    );"""
try:
    with closing(sqlite3.connect(db)) as conn:
        cursor = conn.cursor()

        cursor.execute(create_table_query)
        conn.commit()
        print("Table created successfully.")

except sqlite3.OperationalError as e:
    print(f"Failed to create table: {e}")
    raise HTTPException(status_code=500, detail={"error": "Failed to create table."})


# Seeds three tasks if table is empty
def seed_tasks(db):
    sample_tasks = [
        ("Stretch your body", 0),
        ("Feed your cats", 0),
        ("Drink a full glass of water", 0),
    ]

    with closing(sqlite3.connect(db)) as conn:
        cursor = conn.cursor()
        is_empty = cursor.execute("SELECT 1 FROM tasks LIMIT 1").fetchone() is None

        if is_empty:
            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                sample_tasks,
            )
            conn.commit()


# Runs once at startup, after the table has been created
seed_tasks(db)


# API requests
@app.get("/")
async def root():
    return {"message": "hello world"}


@app.get("/api")
async def describe_api():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
async def health():
    return {"status": "ok"}


# Tasks API requests
@app.get("/tasks")
async def get_all_task():
    try:
        with closing(sqlite3.connect(db)) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM tasks")

            tasks = cursor.fetchall()
            print("Tasks fetched succesfully.")

            if tasks is None:
                raise HTTPException(
                    status_code=404, detail={"error": "Tasks not found"}
                )

            return tasks

    except sqlite3.OperationalError as e:
        print(f"Error 500: Database error: {e}")
        raise HTTPException(status_code=500, detail={"error": "Database error"})


@app.get("/tasks/{id}")
async def get_task(id: int):
    try:
        with closing(sqlite3.connect(db)) as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT * FROM tasks WHERE id == ?", (id,))

            task = cursor.fetchone()
            print("Tasks fetched succesfully.")

            if task is None:
                raise HTTPException(status_code=404, detail={"error": "Task not found"})

            return task

    except sqlite3.OperationalError as e:
        print(f"Error 500: Database error: {e}")
        raise HTTPException(status_code=500, detail={"error": "Database error"})


@app.post("/tasks", status_code=201)
async def create_task(task: taskCreate):
    if not task.title or not task.title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is empty."})

    insert_task(db, (task.title, 0))
    id = cursor.lastrowid

    return {"id": id, "title": task.title, "done": 0}


# @app.put("/tasks/{id}", response_model=taskOut)
# async def update(id: int, task: taskChange):
#     if not task.title or not task.title.strip():
#         return JSONResponse(status_code=400, content={"error": "Title is empty"})

#     for item in task_objects:
#         if item["id"] == id:
#             item["title"] = task.title
#             item["done"] = task.done
#             return item

#     return JSONResponse(status_code=404, content={"error": "Task not found."})


# @app.delete("/tasks/{id}", status_code=204)
# async def delete(id: int):
#     for i, item in enumerate(task_objects):
#         if item["id"] == id:
#             task_objects.pop(i)
#             return

#     return JSONResponse(status_code=404, content={"error": "Task not found."})
