from typing import List, Optional
from database import db
from schemas import VideoCreate, VideoCommentCreate
import logging
import urllib.parse

logger = logging.getLogger(__name__)

import re
import html
import urllib.request

def extract_video_key(url: str) -> Optional[str]:
    """
    Extracts the YouTube video ID from a URL.
    """
    if not url:
        return None
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed.path == '/watch':
                qs = urllib.parse.parse_qs(parsed.query)
                return qs.get('v', [None])[0]
            elif parsed.path.startswith('/embed/'):
                return parsed.path.split('/')[2]
        elif parsed.hostname == 'youtu.be':
            return parsed.path[1:]
    except Exception:
        pass
    return None

def get_video_title_service(url: str) -> Optional[str]:
    try:
        # User-Agent header is required to avoid 403 Forbidden on some sites
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8', errors='ignore')
            
            # Simple regex to find title tag
            match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if match:
                title = match.group(1).strip()
                # Decode HTML entities (e.g. &amp; -> &)
                title = html.unescape(title)
                # Remove " - YouTube" suffix if present
                title = title.replace(" - YouTube", "")
                return title
    except Exception as e:
        logger.error(f"Failed to fetch title for {url}: {e}")
        return None
    return None

async def create_video_service(video: VideoCreate, author_id: int) -> dict:
    ctx = await db.get_connection()
    async with ctx as conn:
        try:
            video_key = extract_video_key(video.url)
            
            # Fetch original title from YouTube
            original_title = get_video_title_service(video.url)
            if not original_title:
                original_title = video.title

            row = await conn.fetchrow("""
                INSERT INTO videos (title, original_title, description, url, video_key, tag_id, uploader_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id, title, original_title, description, url, video_key, view_count, like_count, hate_count, reported_count, tag_id, uploader_id, created_at
            """, video.title, original_title, video.description, video.url, video_key, video.tag_id, author_id)
            
            # Fetch author name and tag name
            author_row = await conn.fetchrow("SELECT nick_name FROM users WHERE id = $1", author_id)
            author_name = author_row['nick_name'] if author_row else "Unknown"

            tag_name = None
            if video.tag_id:
               tag_row = await conn.fetchrow("SELECT name FROM video_tags WHERE id = $1", video.tag_id)
               tag_name = tag_row['name'] if tag_row else None

            return {**dict(row), "author": author_name, "tag_name": tag_name, "comments": []}
        except Exception as e:
            logger.error(f"Error in create_video_service: {e}")
            raise e

async def get_videos_service(page: int = 1, limit: int = 10) -> dict:
    ctx = await db.get_connection()
    async with ctx as conn:
        try:
            offset = (page - 1) * limit
            
            # Get Total Count
            count_row = await conn.fetchrow("SELECT count(*) FROM videos")
            total = count_row[0]
            
            # Get Videos with Author and Tag Name
            query = """
                SELECT v.*, u.nick_name as author, t.name as tag_name
                FROM videos v
                LEFT JOIN users u ON v.uploader_id = u.id
                LEFT JOIN video_tags t ON v.tag_id = t.id
                ORDER BY v.created_at DESC
                LIMIT $1 OFFSET $2
            """
            rows = await conn.fetch(query, limit, offset)
            
            videos = []
            for row in rows:
                video_data = dict(row)
                video_id = video_data['id']
                
                # Fetch comments
                c_rows = await conn.fetch("""
                    SELECT c.id, c.content, c.created_at, c.reply_id, u.nick_name as author
                    FROM video_comments c
                    LEFT JOIN users u ON c.user_id = u.id
                    WHERE c.video_id = $1
                    ORDER BY c.created_at ASC
                """, video_id)
                
                comments = [dict(c) for c in c_rows]
                video_data['comments'] = comments
                videos.append(video_data)
                
            return {"total": total, "videos": videos}
        except Exception as e:
            logger.error(f"Error in get_videos_service: {e}")
            raise e

async def get_video_tags_service() -> List[dict]:
    ctx = await db.get_connection()
    async with ctx as conn:
        try:
            rows = await conn.fetch("SELECT id, name FROM video_tags ORDER BY id ASC")
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error in get_video_tags_service: {e}")
            raise e

async def create_comment_service(video_id: int, user_id: int, comment: VideoCommentCreate) -> dict:
     ctx = await db.get_connection()
     async with ctx as conn:
        try:
            row = await conn.fetchrow("""
                INSERT INTO video_comments (video_id, user_id, content, reply_id)
                VALUES ($1, $2, $3, $4)
                RETURNING id, content, created_at, reply_id, video_id
            """, video_id, user_id, comment.content, comment.reply_id)
            
            author_row = await conn.fetchrow("SELECT nick_name FROM users WHERE id = $1", user_id)
            author_name = author_row['nick_name'] if author_row else "Unknown"
            
            return {**dict(row), "author": author_name}
        except Exception as e:
            logger.error(f"Error in create_comment_service: {e}")
            raise e

async def delete_comment_service(comment_id: int, user_id: int) -> bool:
    ctx = await db.get_connection()
    async with ctx as conn:
        try:
            # Check ownership logic (omitted for brevity, can add later)
            result = await conn.execute("DELETE FROM video_comments WHERE id = $1 AND user_id = $2", comment_id, user_id)
            return result != "DELETE 0"
        except Exception as e:
            logger.error(f"Error in delete_comment_service: {e}")
            raise e

async def update_video_metric_service(video_id: int, metric: str, delta: int) -> dict:
    ctx = await db.get_connection()
    async with ctx as conn:
        try:
            # Validate metric name to prevent SQL injection
            allowed_metrics = ['view_count', 'like_count', 'hate_count', 'reported_count']
            if metric not in allowed_metrics:
                raise Exception("Invalid metric")

            query = f"""
                UPDATE videos
                SET {metric} = {metric} + $1
                WHERE id = $2
                RETURNING id, {metric}
            """
            row = await conn.fetchrow(query, delta, video_id)
            if not row:
                raise Exception("Video not found")
            return dict(row)
        except Exception as e:
            logger.error(f"Error in update_video_metric_service: {e}")
            raise e

async def delete_video_service(video_id: int, user: dict) -> bool:
    ctx = await db.get_connection()
    async with ctx as conn:
        try:
            # Check ownership logic
            video = await conn.fetchrow("SELECT uploader_id FROM videos WHERE id = $1", video_id)
            if not video:
                 return False # Or raise not found
            
            # user object implies dict or object from UserResponse. Assuming dict from controller/router context or object.
            # Based on UserResponse schema: user.id, user.check_admin
            # If user is passed as Pydantic model or dict. Let's assume Pydantic model or allow access.
            # Safest is to handle both or expect object. Router returns UserResponse model.
            
            # Check permissions: Owner or Admin
            if video['uploader_id'] != user.id and not user.check_admin:
                 raise Exception("Permission denied")

            result = await conn.execute("DELETE FROM videos WHERE id = $1", video_id)
            return result != "DELETE 0"
        except Exception as e:
            logger.error(f"Error in delete_video_service: {e}")
            raise e
