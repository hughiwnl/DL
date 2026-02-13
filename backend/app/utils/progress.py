import json

import redis

from app.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)


def set_progress(download_id: str, data: dict) -> None:
    payload = json.dumps(data)
    redis_client.set(f"dl:progress:{download_id}", payload, ex=3600)
    redis_client.publish(f"dl:progress:{download_id}", payload)


def get_progress(download_id: str) -> dict | None:
    raw = redis_client.get(f"dl:progress:{download_id}")
    if raw:
        return json.loads(raw)
    return None
