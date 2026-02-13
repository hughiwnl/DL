import json

import redis

from app.config import settings

# TTL for all job data — auto-expires after 10 minutes
JOB_TTL = 600

redis_client = redis.Redis.from_url(settings.REDIS_URL)


def set_progress(download_id: str, data: dict) -> None:
    payload = json.dumps(data)
    redis_client.set(f"dl:progress:{download_id}", payload, ex=JOB_TTL)
    redis_client.publish(f"dl:progress:{download_id}", payload)


def get_progress(download_id: str) -> dict | None:
    raw = redis_client.get(f"dl:progress:{download_id}")
    if raw:
        return json.loads(raw)
    return None


def set_job(download_id: str, data: dict) -> None:
    redis_client.set(f"dl:job:{download_id}", json.dumps(data), ex=JOB_TTL)


def get_job(download_id: str) -> dict | None:
    raw = redis_client.get(f"dl:job:{download_id}")
    if raw:
        return json.loads(raw)
    return None


def delete_job(download_id: str) -> None:
    redis_client.delete(f"dl:job:{download_id}")
    redis_client.delete(f"dl:progress:{download_id}")
