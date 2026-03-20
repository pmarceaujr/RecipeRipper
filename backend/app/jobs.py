# app/jobs.py
"""
Lightweight Redis-backed job store.

Each job is a JSON blob stored at  job:<uuid>  with a 1-hour TTL.
Shape:
    pending  →  {"status": "pending"}
    done     →  {"status": "done", "recipe_id": <int>, "title": <str>}
    error    →  {"status": "error", "error": <str>}

Usage:
    job_id = create_job()                          # call before spawning thread
    set_result(job_id, {"recipe_id": 42, ...})     # call inside thread on success
    set_error(job_id, "something went wrong")      # call inside thread on failure
    job = get_job(job_id)                          # call from the polling endpoint
"""

import json
import os
import uuid

import redis

_redis = redis.from_url(os.environ["REDIS_URL"], decode_responses=True)

# How long (seconds) a completed or failed job result lives in Redis.
# Pending jobs also use this TTL — if the dyno dies mid-job the record
# expires automatically rather than staying stuck as "pending" forever.
TTL = 3600  # 1 hour


def create_job() -> str:
    """
    Register a new pending job and return its ID.
    Call this in the request handler before spawning the background thread.
    """
    job_id = str(uuid.uuid4())
    _redis.setex(f"job:{job_id}", TTL, json.dumps({"status": "pending"}))
    return job_id


def set_result(job_id: str, data: dict) -> None:
    """
    Mark a job as successfully completed and store its result payload.
    Call this at the end of the background thread when everything succeeded.
    `data` should contain at minimum {"recipe_id": <int>, "title": <str>}.
    """
    _redis.setex(f"job:{job_id}", TTL, json.dumps({"status": "done", **data}))


def set_error(job_id: str, message: str) -> None:
    """
    Mark a job as failed and store the error message.
    Call this in the except block of the background thread.
    """
    _redis.setex(f"job:{job_id}", TTL, json.dumps({"status": "error", "error": message}))


def get_job(job_id: str) -> dict | None:
    """
    Fetch the current state of a job.
    Returns None if the job_id is unknown or has expired.
    """
    raw = _redis.get(f"job:{job_id}")
    return json.loads(raw) if raw else None