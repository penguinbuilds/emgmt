from fastapi import APIRouter, Depends, HTTPException, Query

router = APIRouter(prefix="/login", tags=["login"])


@router.post("/")
async def login():
    return {"message": "fake-token"}
