from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas
import datetime

def post_message(db, author, data):
    if author.is_banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Banned users can't post")
    
    # in the future we may validate group_id membership when the group model exists

    post = models.Post(author_id=author.id, group_id=data.group_id, content=data.content, created_at=data.posttime)
    db.add(post)
    db.commit()
    db.refresh(post)
    
    # in the future may need to emit a crisis detector for the moderator

    return post

def delete_post(db, user, post_id):
    """Allow users to delete their own posts"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own posts")
    
    if post.status == models.PostStatus.DELETED:
        raise HTTPException(status_code=400, detail="Post is already deleted")
    
    post.status = models.PostStatus.DELETED
    db.commit()
    db.refresh(post)
    
    return post