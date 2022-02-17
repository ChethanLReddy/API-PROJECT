from ast import Not
from statistics import mode
from turtle import pos
from fastapi import Body, Depends, FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils, oauth2
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from app import database

router = APIRouter(
    prefix='/vote',
    tags=['vote']
)


@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.vote, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.post).filter(models.post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'post not found')
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,
                                              models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f'user{current_user.id} has voted on post {vote.post_id}')
        new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id)
        db.add(new_vote)
        db.commit()
        return {'message': 'vote added'}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'vote not found')
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {'message': 'vote deleted'}
