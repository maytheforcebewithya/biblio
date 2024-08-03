from fastapi import FastAPI, Depends, Path, HTTPException, Request
from pydantic import ValidationError
from fastapi.responses import JSONResponse
from exceptions import NotFoundException, InvalidRequestException, DuplicateEntryException, DBIntegrityError
from sqlmodel import Session, select
from datetime import date
import models, schemas, crud
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi.middleware.cors import CORSMiddleware
from routers import author, book, borrows, patron, publisher, bookcopy
from sqlalchemy.exc import DatabaseError
import sys
import logging

app = FastAPI()

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Shutting down...")

@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
    except DuplicateEntryException as e:
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})
    except NotFoundException as e:
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})
    except InvalidRequestException as e:
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})
    except DBIntegrityError as e:
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})
    except DatabaseError as e:
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})
    except ValidationError as e:
        error_details = []
        for error in e.errors():
            error_details.append({
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"]
            })
        return JSONResponse(
            status_code=400,
            content={"message": "Validation error", "details": error_details}
        )
    except ValueError as e:
        return JSONResponse(status_code=400, content={"message": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Internal server error"})
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8051"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patron.router, prefix="/patron", tags=["patron"])
app.include_router(author.router, prefix="/author", tags=["author"])
app.include_router(publisher.router, prefix="/publisher", tags=["publisher"])
app.include_router(book.router, prefix="/book", tags=["book"])
app.include_router(borrows.router, prefix="/borrows", tags=["borrows"])
app.include_router(bookcopy.router, prefix="/bookcopy", tags=["bookcopy"])


def calculate_patron_fines():
    with crud.get_session() as session:
        today = date.today()
        operation = select(models.Borrows).where(models.Borrows.due_date < today).where(models.Borrows.return_date == None)
        overdue_books = session.exec(operation).all()
        for book in overdue_books:
            patron = session.exec(select(models.Patron).where(models.Patron.id == book.patron_id)).one()
            patron.fine += 1
            session.add(patron)
        session.commit()

@app.on_event("startup")
def on_startup():
    logging.info("Starting up...")
    models.SQLModel.metadata.create_all(crud.engine)
    scheduler = BackgroundScheduler()
    scheduler.start()

    scheduler.add_job(
        calculate_patron_fines,
        trigger=CronTrigger(hour=11, minute=22, second=5),
        id='calculate_patron_fines',
        name='Calculate Patron Fines',
        replace_existing=True
    )

@app.get("/")
def greet():
    return {
        "message": "Hello, from biblio!"
    }
