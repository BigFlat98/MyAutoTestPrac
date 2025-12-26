from typing import List, Optional
from database import db
from schemas import TodoCreate, TodoUpdate
import logging

logger = logging.getLogger(__name__)

async def create_todo_service(todo: TodoCreate, author_id: Optional[int] = None) -> dict:
    # get_connection is async and returns the context manager
    ctx = await db.get_connection()
    async with ctx as conn:
        try:
            row = await conn.fetchrow("""
                INSERT INTO todos (title, description, due_date, author_id)
                VALUES ($1, $2, $3, $4)
                RETURNING id, title, description, due_date, is_done, created_at, author_id
            """, todo.title, todo.description, todo.due_date, author_id)
            return dict(row)
        except Exception as e:
            logger.error(f"Error in create_todo_service: {e}")
            raise e

async def get_todos_service() -> List[dict]:
    ctx = await db.get_connection()
    async with ctx as conn:
        try:
            rows = await conn.fetch("SELECT id, title, description, due_date, is_done, created_at, author_id FROM todos ORDER BY created_at DESC")
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error in get_todos_service: {e}")
            raise e

from fastapi import HTTPException, status

async def update_todo_service(todo_id: int, todo: TodoUpdate, user_id: int) -> Optional[dict]:
    ctx = await db.get_connection()
    async with ctx as conn:
        try:
            # 1. Check ownership
            current_todo = await conn.fetchrow("SELECT author_id FROM todos WHERE id = $1", todo_id)
            if not current_todo:
                return None # Will be 404 in router
            
            if current_todo['author_id'] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to update this todo"
                )

            # 2. Update
            row = await conn.fetchrow("""
                UPDATE todos
                SET 
                    title = COALESCE($1, title),
                    description = COALESCE($2, description),
                    due_date = COALESCE($3, due_date),
                    is_done = COALESCE($4, is_done)
                WHERE id = $5
                RETURNING id, title, description, due_date, is_done, created_at, author_id
            """, todo.title, todo.description, todo.due_date, todo.is_done, todo_id)
            
            return dict(row)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in update_todo_service: {e}")
            raise e

async def delete_todo_service(todo_id: int, user_id: int) -> bool:
    ctx = await db.get_connection()
    async with ctx as conn:
        try:
            # 1. Check ownership and admin status
            current_todo = await conn.fetchrow("SELECT author_id FROM todos WHERE id = $1", todo_id)
            if not current_todo:
                return False
            
            # If not author, check if admin
            if current_todo['author_id'] != user_id:
                user_info = await conn.fetchrow("SELECT check_admin FROM users WHERE id = $1", user_id)
                is_admin = user_info['check_admin'] if user_info else False
                
                if not is_admin:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You do not have permission to delete this todo"
                    )

            result = await conn.execute("DELETE FROM todos WHERE id = $1", todo_id)
            if result == "DELETE 0":
                return False
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in delete_todo_service: {e}")
            raise e
