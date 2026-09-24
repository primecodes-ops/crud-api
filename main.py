from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "hello world"}


@app.get("/api")
async def describe_api():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
async def health():
    return {"status": "ok"}
