from datetime import datetime

from beanie import PydanticObjectId

from app.models import Item, User
from app.schemas import ItemCreate, ItemUpdate
from app.utils import hash_password, verify_password



async def create_user(username: str, email: str, password: str):
    if await User.find_one(User.username == username):
        raise ValueError("username already exists")
    hashed = hash_password(password)
    user = User(username=username, email=email, hashed_password=hashed)
    await user.insert()
    return user


async def authenticate_user(username: str, password: str):
    """Authenticate user by username and password"""
    user = await User.find_one(User.username == username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def create_item(data: ItemCreate, owner_id: str):
    item = Item(**data.model_dump(), owner_id=owner_id)
    await item.insert()
    return item


async def get_item(item_id: str):
    return await Item.get(PydanticObjectId(item_id))


async def update_item(item_id: str, data: ItemUpdate):
    item = await get_item(item_id)
    if not item or item.deleted:
        return None
    update_payload = {k: v for k, v in data.model_dump().items() if v is not None}
    if update_payload:
        update_payload["updated_at"] = datetime.utcnow()
        await item.set(update_payload)
        await item.save()
    return item


async def soft_delete_item(item_id: str):
    item = await get_item(item_id)
    if not item or item.deleted:
        return None
    item.deleted = True
    await item.save()
    return True


async def hard_delete_item(item_id: str):
    item = await get_item(item_id)
    if not item:
        return None
    await item.delete()
    return True


async def list_items(include_deleted: bool = False, skip: int = 0, limit: int = 50):
    if include_deleted:
        q = Item.find_all()
    else:
        q = Item.find({"deleted": False})
    return await q.skip(skip).limit(limit).to_list()
