import motor.motor_asyncio
from config import Config
from .utils import send_log

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users_col = self.db.users

    def new_user(self, id):
        return dict(
            _id=int(id),
            email=None,
            token=None,
            limit=None,
            used=0
        )

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            await self.users_col.insert_one(user)
            await send_log(b, u)

    async def is_user_exist(self, id):
        user = await self.users_col.find_one({'_id': int(id)})
        return bool(user)

    async def get_data(self, user_id, keys):
        user = await self.users_col.find_one({"_id": int(user_id)}, {key: 1 for key in keys})
        if user:
            return {key: user.get(key) for key in keys}
        return {key: None for key in keys}

    async def save_data(self, user_id, data):
        await self.users_col.update_one(
            {"_id": int(user_id)},
            {"$set": data},
            upsert=True
        )

    async def total_users_count(self):
        count = await self.users_col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.users_col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.users_col.delete_many({'_id': int(user_id)})

db = Database(Config.DB_URL, Config.DB_NAME)
