from fastapi import FastAPI, Depends, Path, HTTPException, APIRouter
from sqlmodel import Session
import models, schemas, crud

router = APIRouter()

@router.get("/count")
def get_patron_count(session: Session = Depends(crud.get_session)):
    return crud.count_bookcopies(session)

@router.get("/overdue")
def overdue_bookcopies(session: Session = Depends(crud.get_session)):
    return crud.get_overdue_bookcopies(session)

@router.get("/available")
def available_bookcopies(session: Session = Depends(crud.get_session)):
    return crud.get_available_bookcopies(session)

@router.get("/unreturnedcount")
def get_unreturned_count(session: Session = Depends(crud.get_session)):
    return crud.count_unreturned_bookcopies(session)