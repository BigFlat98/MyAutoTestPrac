from fastapi import HTTPException, status, UploadFile
from typing import List, Optional
from database import db
from schemas import PostResponse, CommentResponse, CommentCreate, PostCreate
from datetime import datetime
import os
import shutil
import uuid

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

async def upload_image(file: UploadFile, current_user) -> dict:
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Ensure dir exists
    if not os.path.exists(UPLOAD_DIR):
         os.makedirs(UPLOAD_DIR)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    image_url = f"/static/{filename}"
    return {"url": image_url}

async def get_posts(page: int, limit: int) -> dict:
    offset = (page - 1) * limit
    
    async with db.pool.acquire() as conn:
        # Get Total Count
        total = await conn.fetchval("SELECT COUNT(*) FROM posts")
        
        query = """
            SELECT p.id, p.title, p.description, p.view_count, p.created_at, u.nick_name as author, p.author_id, i.image_location as image
            FROM posts p
            JOIN users u ON p.author_id = u.id
            LEFT JOIN post_images i ON p.id = i.post_id
            ORDER BY p.created_at DESC
            LIMIT $1 OFFSET $2
        """
        rows = await conn.fetch(query, limit, offset)
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "posts": [dict(row) for row in rows]
        }

async def get_post(post_id: int) -> dict:
    query = """
        SELECT p.id, p.title, p.description, p.view_count, p.created_at, u.nick_name as author, p.author_id, i.image_location as image
        FROM posts p
        JOIN users u ON p.author_id = u.id
        LEFT JOIN post_images i ON p.id = i.post_id
        WHERE p.id = $1
    """
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(query, post_id)
        if not row:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Increment view count
        await conn.execute("UPDATE posts SET view_count = view_count + 1 WHERE id = $1", post_id)
        
        return dict(row)

async def create_post(
    title: str,
    description: str,
    is_public: bool,
    image: Optional[UploadFile],
    current_user
) -> PostResponse:
    async with db.pool.acquire() as conn:
        # Insert Post
        post_id = await conn.fetchval(
            """
            INSERT INTO posts (title, description, is_public, author_id)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            title, description, is_public, current_user.id
        )
        
        image_url = None
        if image:
            filename = f"{uuid.uuid4()}_{image.filename}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            # Ensure safe execution even if UPLOAD_DIR check elsewhere fails
            if not os.path.exists(UPLOAD_DIR):
                 os.makedirs(UPLOAD_DIR)
                 
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            # Assuming mounted at /static in main.py
            image_url = f"/static/{filename}" 
            
            await conn.execute(
                """
                INSERT INTO post_images (image_name, image_location, uploader_id, post_id)
                VALUES ($1, $2, $3, $4)
                """,
                image.filename, image_url, current_user.id, post_id
            )

        return PostResponse(
            id=post_id,
            title=title,
            description=description,
            view_count=0,
            author=current_user.nick_name,
            created_at=datetime.now(),
            image=image_url
        )

async def update_post(
    post_id: int,
    title: str,
    description: str,
    is_public: bool,
    image: Optional[UploadFile],
    current_user
) -> PostResponse:
    async with db.pool.acquire() as conn:
        # Check ownership
        post = await conn.fetchrow("SELECT author_id FROM posts WHERE id = $1", post_id)
        if not post:
             raise HTTPException(status_code=404, detail="Post not found")
        if post['author_id'] != current_user.id and not current_user.check_admin:
             raise HTTPException(status_code=403, detail="Not authorized")

        await conn.execute(
            """
            UPDATE posts 
            SET title = $1, description = $2, is_public = $3, modified_at = CURRENT_TIMESTAMP
            WHERE id = $4
            """,
            title, description, is_public, post_id
        )
        
        # Get existing image URL first
        current_image_url = await conn.fetchval("SELECT image_location FROM post_images WHERE post_id = $1", post_id)
        image_url = current_image_url

        if image:
            filename = f"{uuid.uuid4()}_{image.filename}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            image_url = f"/static/{filename}"
            
            # Upsert image
            exists = await conn.fetchval("SELECT id FROM post_images WHERE post_id = $1", post_id)
            if exists:
                await conn.execute("UPDATE post_images SET image_location = $1, image_name = $2 WHERE post_id = $3", image_url, image.filename, post_id)
            else:
                await conn.execute("INSERT INTO post_images (image_name, image_location, uploader_id, post_id) VALUES ($1, $2, $3, $4)", image.filename, image_url, current_user.id, post_id)
        
        return PostResponse(
            id=post_id,
            title=title,
            description=description,
            view_count=0, # In reality we might want to fetch the real view count
            author=current_user.nick_name,
            created_at=datetime.now(), # In reality we might want to fetch original created_at
            image=image_url
        )

async def delete_post(post_id: int, current_user):
    async with db.pool.acquire() as conn:
        post = await conn.fetchrow("SELECT author_id FROM posts WHERE id = $1", post_id)
        if not post:
             raise HTTPException(status_code=404, detail="Post not found")
        if post['author_id'] != current_user.id and not current_user.check_admin:
             raise HTTPException(status_code=403, detail="Not authorized")
        
        await conn.execute("DELETE FROM posts WHERE id = $1", post_id)
        return {"message": "Post deleted"}

async def get_comments(post_id: int) -> List[dict]:
    query = """
        SELECT r.id, r.description as content, r.created_at, u.nick_name as author, r.user_id, r.reply_id
        FROM post_replies r
        JOIN users u ON r.user_id = u.id
        WHERE r.post_id = $1 AND r.delete_at IS NULL
        ORDER BY r.created_at DESC
    """
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, post_id)
        
        # Build Tree
        comments_map = {}
        root_comments = []
        
        # First pass: create nodes
        for row in rows:
            comment_dict = dict(row)
            comment_dict['replies'] = []
            comments_map[comment_dict['id']] = comment_dict
        
        # Second pass: link repies
        for row in rows:
            comment = comments_map[row['id']]
            if row['reply_id'] and row['reply_id'] in comments_map:
                comments_map[row['reply_id']]['replies'].append(comment)
            else:
                root_comments.append(comment)
                
        return root_comments

async def create_comment(
    post_id: int,
    comment: CommentCreate,
    current_user
) -> CommentResponse:
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO post_replies (description, post_id, user_id, reply_id)
            VALUES ($1, $2, $3, $4)
            RETURNING id, created_at
            """,
            comment.description, post_id, current_user.id, comment.reply_id
        )
        
        return CommentResponse(
            id=row['id'],
            content=comment.description,
            author=current_user.nick_name,
            created_at=row['created_at'],
            replies=[]
        )

async def delete_comment(comment_id: int, current_user):
    async with db.pool.acquire() as conn:
        comment = await conn.fetchrow("SELECT user_id FROM post_replies WHERE id = $1", comment_id)
        if not comment:
             raise HTTPException(status_code=404, detail="Comment not found")
        if comment['user_id'] != current_user.id and not current_user.check_admin:
             raise HTTPException(status_code=403, detail="Not authorized")
        
        await conn.execute("UPDATE post_replies SET delete_at = CURRENT_TIMESTAMP WHERE id = $1", comment_id)
        return {"message": "Comment deleted"}
