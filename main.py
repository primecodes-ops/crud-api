from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from contextlib import closing
import sqlite3

# Initializing FastAPI()
app = FastAPI()

# Path to the SQLite database file (created automatically if missing)
db = "tasks.db"


# Creating task BaseModel
class taskCreate(BaseModel):
    title: str


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


# Update task function
def update_task(db, id, data):
    try:
        with closing(sqlite3.connect(db)) as conn:
            cursor = conn.cursor()

            # Update task
            cursor.execute(
                """UPDATE tasks
                SET title = ?, done = ?
                WHERE id = ?;""",
                (*data, id),
            )
            conn.commit()

    except sqlite3.OperationalError as e:
        print(f"Error 500: Database error: {e}")
        raise HTTPException(status_code=500, detail={"error": "Database error"})


# Delete task function
def delete_task(db, id):
    try:
        with closing(sqlite3.connect(db)) as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM tasks WHERE id = ?;", (id,))
            conn.commit()

    except sqlite3.OperationalError as e:
        print(f"Error 500: Database error: {e}")
        raise HTTPException(status_code=500, detail={"error": "Database error"})


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


# Get all tasks
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


# Get task using id
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


# Get the database's statistics
@app.get("/stats")
async def get_stats():
    try:
        with closing(sqlite3.connect(db)) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM tasks;")

            stats = cursor.fetchall()
            print("tasks Table statistics returned succesfully.")

            return stats

    except sqlite3.OperationalError as e:
        print(f"Error 500: Database error: {e}")
        raise HTTPException(status_code=500, detail={"error": "Database error"})


# Create task
@app.post("/tasks", status_code=201)
async def create_task(task: taskCreate):
    if not task.title or not task.title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is empty."})

    insert_task(db, (task.title, 0))
    print("Task created succesfully.")
    id = cursor.lastrowid

    return {"id": id, "title": task.title, "done": 0}


# Update a task
@app.put("/tasks/{id}")
async def update(id: int, task: taskChange):
    if not task.title or not task.title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is empty."})

    update_task(db, id, (task.title, task.done))
    print("Task updated succesfully.")

    return {"id": id, "title": task.title, "done": task.done}


# Delete task
@app.delete("/tasks/{id}", status_code=204)
async def delete(id: int):
    if not id:
        return JSONResponse(
            status_code=400, content={"error": "ID should be of int type."}
        )

    delete_task(db, id)
    print("Task deleted succesfully.")
