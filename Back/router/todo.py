from fastapi import APIRouter, HTTPException, Request
from typing import List
from schemas import TodoCreate, TodoUpdate, TodoResponse
from controller.todo.service import (
    create_todo_service, 
    get_todos_service, 
    update_todo_service, 
    delete_todo_service
)
import logging

# Logger setup
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/todos", tags=["todos"])

@router.post("", response_model=TodoResponse)
async def create_todo(todo: TodoCreate, request: Request):
    try:
        user_id = request.session.get("user_id")
        return await create_todo_service(todo, author_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[TodoResponse])
async def read_todos():
    try:
        return await get_todos_service()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo: TodoUpdate, request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
         raise HTTPException(status_code=401, detail="Not authenticated")
         
    try:
        result = await update_todo_service(todo_id, todo, user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Todo not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
         raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        success = await delete_todo_service(todo_id, user_id)
        if not success:
             raise HTTPException(status_code=404, detail="Todo not found")
        return {"status": "success", "id": todo_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
