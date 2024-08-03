from fastapi import FastAPI, Depends, Path, HTTPException, APIRouter
from sqlmodel import Session
import models, schemas, crud

router = APIRouter()

@router.post("/")
def create_author(author: schemas.CreateAuthor, session: Session = Depends(crud.get_session)):
    return crud.create_author(author, session)

@router.get("/all")
def show_books(session: Session = Depends(crud.get_session)):
    return crud.get_all_authors(session)

@router.get("/count")
def get_patron_count(session: Session = Depends(crud.get_session)):
    return crud.count_authors(session)

@router.get("/name/{author_name}")
def show_authors_by_name(author_name: str, session: Session = Depends(crud.get_session)):
    return crud.get_author_by_name(author_name, session)

@router.patch("/{author_id}")
def update_author(body: schemas.UpdateAuthor, author_id: int, session: Session = Depends(crud.get_session)):
    return crud.update_author(body, author_id, session)

@router.delete("/{author_id}")
def delete_author(author_id: int, session: Session = Depends(crud.get_session)):
    return crud.delete_author(author_id, session)