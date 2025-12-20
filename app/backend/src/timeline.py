import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db import get_async_session
from src.models import (
    TimelinePost, TimelinePostCreate, TimelinePostRead, 
    TimelineReaction, TimelineFeedResponse, User
)
from src.auth import current_active_user

router = APIRouter()

# 1. 投稿を取得（タイムライン表示） - ページネーション & リアクション付き
@router.get("/posts", response_model=List[TimelineFeedResponse])
async def get_timeline(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    # Query: TimelinePost + User (Author)
    stmt = (
        select(TimelinePost, User)
        .join(User, TimelinePost.user_id == User.id)
        .order_by(TimelinePost.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    posts_with_users = result.all() # [(TimelinePost, User), ...]
    
    response = []
    for post, author in posts_with_users:
        # Get Like Count
        likes_count_stmt = select(func.count(TimelineReaction.id)).where(TimelineReaction.post_id == post.id)
        likes_count_res = await db.execute(likes_count_stmt)
        likes_count = likes_count_res.scalar() or 0
        
        # Get My Reaction
        my_reaction_stmt = select(TimelineReaction.reaction_type).where(
            TimelineReaction.post_id == post.id,
            TimelineReaction.user_id == user.id
        )
        my_reaction_res = await db.execute(my_reaction_stmt)
        my_reaction = my_reaction_res.scalar_one_or_none()
        
        response.append(TimelineFeedResponse(
            post=post,
            user=author,
            likes=likes_count,
            my_reaction=my_reaction
        ))
        
    return response

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
    result = await db.execute(select(TimelinePost).where(TimelinePost.id == post_id))
    db_post = result.scalars().first()
    
    if db_post is None:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")
    
    if db_post.user_id != user.id:
        raise HTTPException(status_code=403, detail="Cannot delete other user's post")
    
    await db.delete(db_post)
    await db.commit()

# 4. リアクション追加/更新
@router.post("/posts/{post_id}/reactions", status_code=status.HTTP_200_OK)
async def react_to_post(
    post_id: uuid.UUID,
    reaction_type: str = Query(..., regex="^(point|thumbsUp|hand|pinch)$"),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    # Check if reaction exists
    result = await db.execute(select(TimelineReaction).where(
        TimelineReaction.post_id == post_id,
        TimelineReaction.user_id == user.id
    ))
    existing_reaction = result.scalars().first()
    
    if existing_reaction:
        existing_reaction.reaction_type = reaction_type
    else:
        new_reaction = TimelineReaction(
            user_id=user.id,
            post_id=post_id,
            reaction_type=reaction_type
        )
        db.add(new_reaction)
    
    await db.commit()
    return {"status": "success", "reaction": reaction_type}

# 5. リアクション削除
@router.delete("/posts/{post_id}/reactions", status_code=status.HTTP_204_NO_CONTENT)
async def remove_reaction(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    result = await db.execute(select(TimelineReaction).where(
        TimelineReaction.post_id == post_id,
        TimelineReaction.user_id == user.id
    ))
    existing_reaction = result.scalars().first()
    
    if existing_reaction:
        await db.delete(existing_reaction)
        await db.commit()