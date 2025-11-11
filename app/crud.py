from beanie import PydanticObjectId
from fastapi import HTTPException, status

from app.models import Item, User
from app.schemas import ItemCreate, ItemUpdate
from app.utils import hash_password, verify_password


async def create_user(username: str, email: str, password: str):
    try:
        hash = hash_password(password)
        user = User(username=username, email=email, hashed_password=hash)
        await user.insert()
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def authenticate_user(username: str, password: str):
    try:
        user = await User.find_one(User.username == username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def create_item(data: ItemCreate, owner_id: str):
    try:
        item = Item(**data.model_dump(), owner_id=owner_id)
        await item.insert()
        return item
    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def get_item(item_id: str):
    try:
        return await Item.get(PydanticObjectId(item_id))

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def update_item(item_id: str, data: ItemUpdate):
    try:
        item = await get_item(item_id)
        if not item or item.deleted:
            return None
        update_payload = {k: v for k, v in data.model_dump().items() if v is not None}
        if update_payload:
            update_payload["updated_at"] = __import__("datetime").datetime.utcnow()
            await item.set(update_payload)
            await item.save()
        return item

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def soft_delete_item(item_id: str):
    try:
        item = await get_item(item_id)
        if not item or item.deleted:
            return None
        item.deleted = True
        await item.save()
        return True
    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def hard_delete_item(item_id: str):
    try:
        item = await get_item(item_id)
        if not item:
            return None
        await item.delete()
        return True
    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def list_items(include_deleted: bool = False, skip: int = 0, limit: int = 50):
    try:
        q = Item.find_all()
        if not include_deleted:
            q = Item.find(not Item.deleted)
        return await q.skip(skip).limit(limit).to_list()
    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
