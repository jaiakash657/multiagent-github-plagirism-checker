import redis
from config.settings import settings

cache = redis.Redis.from_url(settings.CELERY_RESULT_BACKEND)

def cache_set(key: str, value: str, expire: int = 3600):
    cache.set(key, value, ex=expire)

def cache_get(key: str):
    data = cache.get(key)
    return data.decode("utf-8") if data else None
