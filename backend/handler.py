from fastapi import FastAPI
from mangum import Mangum
from backend.auth import router as auth_router
from backend.client import router as client_router


app = FastAPI()
app.include_router(auth_router, prefix="/auth")
app.include_router(client_router, prefix="/client")


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


handler = Mangum(app)
