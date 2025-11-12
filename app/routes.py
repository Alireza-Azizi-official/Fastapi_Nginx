from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import create_jwt, get_current_user, require_superuser
from app.crud import (
    authenticate_user,
    create_item,
    create_user,
    get_item,
    hard_delete_item,
    list_items,
    soft_delete_item,
    update_item,
)
from app.models import User
from app.schemas import ItemCreate, ItemUpdate, Token, UserCreate

router = APIRouter()


@router.post("/auth/register", response_model=Token)
async def register(payload: UserCreate):
    try:
        user = await create_user(payload.username, payload.email, payload.password)
    except ValueError:
        raise HTTPException(status_code=400, detail="username already exists")
    token = create_jwt(str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.post("/auth/token", response_model=Token)
async def login(payload: UserCreate):
    user = await authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
        )
    token = create_jwt(str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.post("/items", status_code=201)
async def create_item_endpoint(
    payload: ItemCreate, current_user: User = Depends(get_current_user)
):
    item = await create_item(payload, owner_id=str(current_user.id))
    return item


@router.get("/items")
async def list_items_endpoint(
    skip: int = 0, limit: int = 50, current_user: User = Depends(get_current_user)
):
    return await list_items(skip=skip, limit=limit)


@router.get("/items/{item_id}")
async def get_item_by_id(item_id: str, current_user: User = Depends(get_current_user)):
    item = await get_item(item_id)
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="not found")
    return item


@router.patch("/items/{item_id}")
async def update_item_endpoint(
    item_id: str, payload: ItemUpdate, current_user: User = Depends(get_current_user)
):
    item = await update_item(item_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="not found or deleted")
    return item


@router.delete("/items/{item_id}")
async def soft_delete_endpoint(
    item_id: str, current_user: User = Depends(get_current_user)
):
    ok = await soft_delete_item(item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}


@router.delete("/items/{item_id}/hard")
async def hard_delete_endpoint(
    item_id: str, current_user: User = Depends(require_superuser)
):
    ok = await hard_delete_item(item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"hard_deleted": True}
