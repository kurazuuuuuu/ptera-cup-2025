from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List

# --- DB設定 ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./timeline.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- モデル (DB) ---
class PostModel(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)

# --- スキーマ (バリデーション) ---
class PostCreate(BaseModel):
    username: str
    content: str

class PostResponse(BaseModel):
    id: int
    username: str
    content: str
    created_at: datetime
    class Config:
        from_attributes = True

# --- アプリ本体 ---
# --- アプリ本体 (Router) ---
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- エンドポイント ---

# 1. 投稿を取得（タイムライン表示）
@router.get("/posts", response_model=List[PostResponse])
def get_timeline(db: Session = Depends(get_db)):
    return db.query(PostModel).order_by(PostModel.created_at.desc()).all()

# 2. 新規投稿
@router.post("/posts", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = PostModel(username=post.username, content=post.content)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# 3. 投稿の削除 ★ここが重要
@router.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    # IDで投稿を検索
    db_post = db.query(PostModel).filter(PostModel.id == post_id).first()
    
    # もし投稿が見つからなければエラーを返す
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"ID {post_id} の投稿は見つかりませんでした。"
        )
    
    # 削除実行
    db.delete(db_post)
    db.commit()
    
    return {"message": f"ID {post_id} の投稿を削除しました。"}