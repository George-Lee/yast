from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def auth_index():
    return {"message": "Hello, auth!"}