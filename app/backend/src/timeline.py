from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db import get_async_session
from src.models import TimelinePost, TimelinePostCreate, TimelinePostRead, User
from src.auth import current_active_user

router = APIRouter()

# 1. 投稿を取得（タイムライン表示）
@router.get("/posts", response_model=List[TimelinePostRead])
async def get_timeline(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    # For now, return all posts or filtered by user? 
    # API Schema says "User's timeline", potentially friends/public?
    # Schema: "TimelinePost" has user_id. 
    # Let's assume for now it returns *all* posts (public timeline) or just user's.
    # Given the context "Timeline", likely all posts or friends.
    # Let's just return all posts sorted by date for now as a simple implementation.
    result = await db.execute(select(TimelinePost).order_by(TimelinePost.created_at.desc()))
    return result.scalars().all()

# 2. 新規投稿
@router.post("/posts", response_model=TimelinePostRead)
async def create_post(
    post: TimelinePostCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    db_post = TimelinePost(
        user_id=user.id,
        event_id=post.event_id,
        content=post.content
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post

# 3. 投稿の削除
@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    # IDで投稿を検索
    result = await db.execute(select(TimelinePost).where(TimelinePost.id == post_id))
    db_post = result.scalars().first()
    
    # もし投稿が見つからなければエラーを返す
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"ID {post_id} の投稿は見つかりませんでした。"
        )
    
    # 権限チェック (自分の投稿しか削除できない)
    if db_post.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他のユーザーの投稿は削除できません。"
        )
    
    # 削除実行
    await db.delete(db_post)
    await db.commit()