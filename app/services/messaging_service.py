from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas

def post_message(db, author, data):
    if author.isbanned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Banned users can't post")
    
    # in the future we msy validate group_id membership when the group model exists

    post = models.Post(author_id=author.id, group_id=data.group_id,content=data.content)
    db.add(post)
    db.commit()
    db.refresh(post)
    
    #in the future may need to emit a crisis detector for the moderator

    return post