from fastapi import FastAPI, Depends, Path, HTTPException, APIRouter
from sqlmodel import Session
import models, schemas, crud

router = APIRouter()

@router.post("/")
def create_book(book: schemas.CreateBook, session: Session = Depends(crud.get_session)):
    return crud.create_book(book, session)

@router.get("/all")
def show_books(session: Session = Depends(crud.get_session)):
    return crud.get_all_books(session)

@router.get("/count")
def get_patron_count(session: Session = Depends(crud.get_session)):
    return crud.count_books(session)

@router.get("/isbn/{isbn}")
def show_books_by_isbn(isbn: str = Path(..., min_length=10, max_length=13), session: Session = Depends(crud.get_session)):
    body = schemas.ReadBook(isbn=isbn)
    return crud.get_book_by_isbn(body, session)

@router.get("/title/{title}")
def show_books_by_title(title: str, session: Session = Depends(crud.get_session)):
    body = schemas.ReadBookByTitle(title=title)
    return crud.get_book_by_title(body, session)

@router.get("/genre/{genre}")
def show_books_by_genre(genre: str, session: Session = Depends(crud.get_session)):
    return crud.get_book_by_genre(genre, session)

@router.get("/author/{author_name}")
def show_books_by_author(author_name: str, session: Session = Depends(crud.get_session)):
    return crud.get_book_by_author(author_name, session)

@router.get("/publisher/{publisher_name}")
def show_books_by_publisher(publisher_name: str, session: Session = Depends(crud.get_session)):
    return crud.get_book_by_publisher(publisher_name, session)

@router.patch("/{isbn}")
def update_book(body: schemas.UpdateBook, isbn: str = Path(..., min_length=10, max_length=13), session: Session = Depends(crud.get_session)):
    isbn_val = schemas.ReadBook(isbn=isbn)
    return crud.update_book(body, isbn_val, session)

@router.delete("/{isbn}")
def delete_book(isbn: str = Path(..., min_length=10, max_length=13), session: Session = Depends(crud.get_session)):
    return crud.delete_book(isbn, session)