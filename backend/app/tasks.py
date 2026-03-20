# app/tasks.py
import os
import uuid
from rq import Queue
from redis import Redis
from app.utils.parser import extract_text_from_image, extract_text_from_pdf, parse_from_file, parse_recipe_text
from app.models import Recipe, db  # Adjust to your actual DB models/session
from flask import current_app

# Connect to Redis using Heroku-provided URL
# Use REDIS_URL if set, fallback to REDIS_TLS_URL (for safety during transition)
redis_url = os.environ.get('REDIS_URL') or os.environ.get('REDIS_TLS_URL')
if not redis_url:
    raise RuntimeError("No Redis URL found in config vars — check heroku config")

redis_conn = Redis.from_url(redis_url)

# Test ping (add this in app init or a debug route)
try:
    redis_conn.ping()
    current_app.logger.info("Redis connection successful")
except Exception as e:
    current_app.logger.error(f"Redis ping failed: {e}")
    raise  # or handle gracefully
queue = Queue(connection=redis_conn, default_timeout=300)  # 5 min timeout per job

def process_recipe_upload(user_id: int, file_path: str, filename: str):
    """Background task: extract text, parse, save to DB, clean up file"""
    try:
        ext = os.path.splitext(filename)[1].lower()

        if ext in {'.jpg', '.jpeg', '.png'}:
            text = extract_text_from_image(file_path)
        elif ext == '.pdf':
            text = extract_text_from_pdf(file_path, filename)
        else:  # .txt or others
            text = parse_from_file(file_path, filename)

        recipe_data = parse_recipe_text(text, recipe_source=filename, is_file=True)

        # Save to DB (adjust to your save_recipe logic)
        recipe = Recipe(
            user_id=user_id,
            title=recipe_data.get('title', 'Untitled'),
            # ... map other fields: ingredients, steps, etc. ...
            raw_text=text,          # optional
            status='completed',
            source=filename
        )
        db.session.add(recipe)
        db.session.commit()

        current_app.logger.info(f"Background job completed for recipe {recipe.id} by user {user_id}")

    except Exception as e:
        current_app.logger.error(f"Background job failed for user {user_id}: {str(e)}")
        # Optional: update a status field to 'failed' if you add one
        db.session.rollback()

    finally:
        # Clean up file even on failure
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as cleanup_err:
                current_app.logger.warning(f"Cleanup failed: {cleanup_err}")