from fastapi import FastAPI, Depends, Path, HTTPException, APIRouter
from sqlmodel import Session
import models, schemas, crud

router = APIRouter()

@router.post("/")
def create_publisher(publisher: schemas.CreatePublisher, session: Session = Depends(crud.get_session)):
    return crud.create_publisher(publisher, session)

@router.get("/all")
def show_publishers(session: Session = Depends(crud.get_session)):
    return crud.get_all_publishers(session)

@router.get("/count")
def get_publisher_count(session: Session = Depends(crud.get_session)):
    return crud.count_publishers(session)

@router.get("/name/{publisher_name}")
def show_publishers_by_name(publisher_name: str, session: Session = Depends(crud.get_session)):
    return crud.get_publisher_by_name(publisher_name, session)

@router.patch("/{publisher_id}")
def update_publisher(body: schemas.UpdatePublisher, publisher_id: int, session: Session = Depends(crud.get_session)):
    return crud.update_publisher(body, publisher_id, session)

@router.delete("/{publisher_id}")
def delete_publisher(publisher_id: int, session: Session = Depends(crud.get_session)):
    return crud.delete_publisher(publisher_id, session)