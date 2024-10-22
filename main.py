import uvicorn
from fastapi import FastAPI
from app.routes.v1 import user_routes
from app.db.database import Base

app = FastAPI()

@app.get("/")
async def hello_world() -> str:
    return "Hello world"

app.include_router(user_routes.user_router)
app.include_router(user_routes.test_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
