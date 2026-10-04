from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from contextlib import closing
import sqlite3

# Initializing FastAPI()
app = FastAPI()

# Path to the SQLite database file (created automatically if missing)
db = "tasks.db"


# Create tasks table
# - id: auto-assigned primary key
# - title: the task's text
# - done: 0 = not done, 1 = done (enforced by the CHECK constraint)
create_table_query = """CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY,
                        title TEXT,
                        done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0,1))
                  );"""

# Create the tasks table at startup.
# IF NOT EXISTS makes this safe to run repeatedly.
# On failure, the error is printed and re-raised so the app does not
# start without a table.
try:
    with closing(sqlite3.connect(db)) as conn:
        cursor = conn.cursor()

        cursor.execute(create_table_query)
        conn.commit()
        print("Table created successfully.")

except sqlite3.OperationalError as e:
    print(f"Failed to create table: {e}")
    raise


# Seeds three tasks if table is empty
def seed_tasks(db):
    """Insert three sample tasks, but only if the tasks table is empty.

    Uses a single connection and a single commit, so seeding is
    all-or-nothing: if any insert fails, none are saved.

    Args:
        db: Path to the SQLite database file.

    Raises:
        sqlite3.Error: If the table is missing, the database is locked,
            or an insert fails. Errors are not caught here so the caller
            can decide how to handle them.
    """

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


# Insert task function
def insert_task(db, query, data):
    """Run a single INSERT query and commit it.

    A general-purpose helper: the caller supplies the query and values.
    Always use ? placeholders for values instead of building the query
    with f-strings, to avoid SQL injection.

    Args:
        db: Path to the SQLite database file.
        query: An INSERT statement with ? placeholders,
            e.g. "INSERT INTO tasks (title, done) VALUES (?, ?)".
        data: A tuple of values matching the placeholders,
            e.g. ("Read a book", 0). A single value needs a trailing
            comma: ("Read a book",).

    Raises:
        sqlite3.Error: If the insert fails (e.g. a CHECK constraint
            violation raises sqlite3.IntegrityError).
    """

    with closing(sqlite3.connect(db)) as conn:
        cursor = conn.cursor()

        # Insert tasks
        cursor.execute(query, data)
        conn.commit()


# API requests
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
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

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
