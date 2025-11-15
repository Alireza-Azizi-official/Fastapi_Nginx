from datetime import datetime

from beanie import PydanticObjectId

from app.models import Item, User
from app.schemas import ItemCreate, ItemUpdate
from app.utils import hash_password, verify_password


async def create_user(
    username: str, email: str, password: str, is_superuser: bool = False
):
    if await User.find_one(User.username == username):
        raise ValueError("username already exists")
    hashed = hash_password(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed,
        is_superuser=is_superuser,
    )
    await user.insert()
    print(f"user created: {user.username}")
    return user


async def authenticate_user(username: str, password: str):
    user = await User.find_one(User.username == username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    print("user authenticated:", user.username)
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
    try:
        obj_id = PydanticObjectId(item_id)
    except Exception:
        return None
    item = await Item.get(obj_id)
    if not item:
        return None
    await item.delete()
    return True


async def list_items(include_deleted: bool = False):
    if include_deleted:
        items = Item.find_all()
    else:
        items = Item.find({"deleted": False})

    items = await items.to_list()
    if not items:
        print("no items found")
    else:
        for index, item in enumerate(items):
            print(f"{index}. {item.model_dump()}")
    return items


async def make_superuser(user_id: str):
    user = await User.get(user_id)
    if not user:
        return None
    await user.update({"$set": {"is_superuser": True}})
    return user


async def get_list_of_users():
    users = await User.find_all().to_list()
    if not users:
        print("no users found")
        return None
    for index, user in enumerate(users):
        print(f"{index}. {user.model_dump()}")
    return users
