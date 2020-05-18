from redis import Redis, StrictRedis

from settings import settings


def redis_connection():
    return Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
