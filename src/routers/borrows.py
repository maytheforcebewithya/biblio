from fastapi import FastAPI, Depends, Path, HTTPException, APIRouter
from sqlmodel import Session
import models, schemas, crud

router = APIRouter()

@router.post("/")
def create_borrow(borrows: schemas.AddBorrow, session: Session = Depends(crud.get_session)):
    return crud.create_borrow(borrows, session)

@router.get("/all")
def show_borrows(session: Session = Depends(crud.get_session)):
    return crud.get_all_borrows(session)

@router.get("/count")
def get_borrow_count(session: Session = Depends(crud.get_session)):
    return crud.count_transactions(session)

@router.put("/return/{transaction_id}")
def return_borrow(transaction_id: int, borrow: schemas.ReturnBorrow, session: Session = Depends(crud.get_session)):
    return crud.return_borrow(transaction_id, borrow, session)

@router.get("/patron/{patron_id}")
def get_borrow_by_patron(patron_id: str = Path(..., min_length=10, max_length=10), session: Session = Depends(crud.get_session)):
    return crud.get_borrows_by_patron(patron_id, session)

@router.get("/isbn/{isbn}")
def get_borrow_by_isbn(isbn: str = Path(..., min_length=10, max_length=13), session: Session = Depends(crud.get_session)):
    return crud.get_borrows_by_isbn(isbn, session)