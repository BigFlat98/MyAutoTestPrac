from typing import List, Optional
from database import db
from schemas import TodoCreate, TodoUpdate
import logging

logger = logging.getLogger(__name__)

async def create_todo_service(todo: TodoCreate) -> dict:
    # get_connection is async and returns the context manager
    ctx = await db.get_connection()
    async with ctx as conn:
        try:
            row = await conn.fetchrow("""
                INSERT INTO todos (title, description, due_date, author)
                VALUES ($1, $2, $3, $4)
                RETURNING id, title, description, due_date, is_done, created_at, author
            """, todo.title, todo.description, todo.due_date, todo.author)
            return dict(row)
        except Exception as e:
            logger.error(f"Error in create_todo_service: {e}")
            raise e

async def get_todos_service() -> List[dict]:
    ctx = await db.get_connection()
    async with ctx as conn:
        try:
            rows = await conn.fetch("SELECT id, title, description, due_date, is_done, created_at, author FROM todos ORDER BY created_at DESC")
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error in get_todos_service: {e}")
            raise e

async def update_todo_service(todo_id: int, todo: TodoUpdate) -> Optional[dict]:
    ctx = await db.get_connection()
    async with ctx as conn:
        try:
            row = await conn.fetchrow("""
                UPDATE todos
                SET 
                    title = COALESCE($1, title),
                    description = COALESCE($2, description),
                    due_date = COALESCE($3, due_date),
                    is_done = COALESCE($4, is_done)
                WHERE id = $5
                RETURNING id, title, description, due_date, is_done, created_at, author
            """, todo.title, todo.description, todo.due_date, todo.is_done, todo_id)
            
            if not row:
                return None
            return dict(row)
        except Exception as e:
            logger.error(f"Error in update_todo_service: {e}")
            raise e

async def delete_todo_service(todo_id: int) -> bool:
    ctx = await db.get_connection()
    async with ctx as conn:
        try:
            result = await conn.execute("DELETE FROM todos WHERE id = $1", todo_id)
            # result is formatted like "DELETE 0" or "DELETE 1"
            if result == "DELETE 0":
                return False
            return True
        except Exception as e:
            logger.error(f"Error in delete_todo_service: {e}")
            raise e
