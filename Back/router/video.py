from fastapi import APIRouter, HTTPException, Request, Query
from typing import List
from schemas import VideoCreate, VideoResponse, VideoListResponse, VideoCommentCreate, VideoCommentResponse, VideoTagResponse
from controller.video.service import create_video_service, get_videos_service, create_comment_service, get_video_tags_service, update_video_metric_service, delete_video_service, get_video_title_service
from controller.auth import auth_controller

router = APIRouter(prefix="/videos", tags=["videos"])

@router.delete("/{video_id}", status_code=204)
async def delete_video(video_id: int, request: Request):
    try:
        current_user = await auth_controller.get_current_user(request)
        if not current_user:
             raise HTTPException(status_code=401, detail="Unauthorized")

        success = await delete_video_service(video_id, current_user)
        if not success:
            raise HTTPException(status_code=404, detail="Video not found")
        return
    except Exception as e:
        if str(e) == "Permission denied":
             raise HTTPException(status_code=403, detail="Permission denied")
        raise e

@router.get("/tags", response_model=List[VideoTagResponse])
async def get_tags():
    try:
        return await get_video_tags_service()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{video_id}/view")
async def increase_view(video_id: int):
    try:
        return await update_video_metric_service(video_id, 'view_count', 1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{video_id}/like")
async def like_video(video_id: int):
    try:
        return await update_video_metric_service(video_id, 'like_count', 1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{video_id}/like")
async def unlike_video(video_id: int):
    try:
        return await update_video_metric_service(video_id, 'like_count', -1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{video_id}/hate")
async def hate_video(video_id: int):
    try:
        return await update_video_metric_service(video_id, 'hate_count', 1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{video_id}/hate")
async def unhate_video(video_id: int):
    try:
        return await update_video_metric_service(video_id, 'hate_count', -1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{video_id}/report")
async def report_video(video_id: int):
    try:
        return await update_video_metric_service(video_id, 'reported_count', 1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=VideoResponse)
async def create_video(video: VideoCreate, request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return await create_video_service(video, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=VideoListResponse)
async def get_videos(request: Request, page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=50), uploader_me: bool = Query(False)):
    try:
        uploader_id = None
        if uploader_me:
            from controller.auth.auth_controller import get_optional_current_user
            current_user = await get_optional_current_user(request)
            if not current_user:
                raise HTTPException(status_code=401, detail="Not authenticated")
            uploader_id = current_user.id
        return await get_videos_service(page=page, limit=limit, uploader_id=uploader_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{video_id}/comments", response_model=VideoCommentResponse)
async def create_comment(video_id: int, comment: VideoCommentCreate, request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return await create_comment_service(video_id, user_id, comment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
