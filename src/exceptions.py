from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound

class DuplicateEntryException(HTTPException):
    def __init__(self, detail: str = "Duplicate entry found"):
        super().__init__(status_code=400, detail=detail)

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)

class InvalidRequestException(HTTPException):
    def __init__(self, detail: str = "Invalid request"):
        super().__init__(status_code=400, detail=detail)

class DBIntegrityError(IntegrityError):
    def __init__(self, detail: str = "Database Integrity compromised. Rollback issued."):
        super().__init__(status_code=500, detail=detail)

class ValueValidationError(ValueError):
    def __init__(self, detail: str = "Generic Pythonic Value Error"):
        super().__init__(status_code=400, detail=detail)