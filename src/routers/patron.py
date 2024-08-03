from fastapi import FastAPI, Depends, Path, HTTPException, APIRouter
from sqlmodel import Session
import models, schemas, crud

router = APIRouter()

@router.post("/")
def create_patron(patron: schemas.CreatePatron, session: Session = Depends(crud.get_session)):
    return crud.create_patron(patron, session)

@router.get("/all")
def show_patrons(session: Session = Depends(crud.get_session)):
    return crud.get_all_patrons(session)

@router.get("/count")
def get_patron_count(session: Session = Depends(crud.get_session)):
    return crud.count_patrons(session)

@router.get("/id/{patron_id}")
def show_patrons_by_id(patron_id: str, session: Session = Depends(crud.get_session)):
    body = schemas.ReadPatron(patron_id=patron_id)
    return crud.get_patron_by_id(body, session)

@router.get("/name/{patron_name}")
def show_patrons_by_name(patron_name, session: Session = Depends(crud.get_session)):
    return crud.get_patron_by_name(patron_name, session)

@router.get("/fine/{fine}")
def show_patrons_by_fine(fine: float, session: Session = Depends(crud.get_session)):
    if fine < 0:
        raise HTTPException(status_code=422, detail='Fine criteria cannot be below 0')
    body = schemas.ReadPatronByFine(patron_fine=fine)
    return crud.get_patron_by_fine(body, session)

@router.get("/finetotal")
def get_total_fine(session: Session = Depends(crud.get_session)):
    return crud.sum_of_patron_fines(session)

@router.patch("/{patron_id}")
def update_patron(body: schemas.UpdatePatron, patron_id: str = Path(..., min_length=10, max_length=10), session: Session = Depends(crud.get_session)):
    return crud.update_patron(body, patron_id, session)

@router.delete("/{patron_id}")
def delete_patron(patron_id: str = Path(..., min_length=10, max_length=10), session: Session = Depends(crud.get_session)):
    return crud.delete_patron(patron_id, session)