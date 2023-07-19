import redis.asyncio as redis

from src.config import settings


class RedisConnector:

    def __init__(self, redis_url):
        self.redis_url = redis_url
        self.redis = None

    async def get_redis_db(self):
        if self.redis is None:
            self.redis = await redis.from_url(self.redis_url)
        return self.redis


redis_db = RedisConnector(settings.redis_database_url)


