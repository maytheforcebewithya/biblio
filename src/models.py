from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from enum import Enum as PyEnum

class PatronStatusEnum(str, PyEnum):
    INACTIVE = "IN"
    ACTIVE = "AC"

class Patron(SQLModel, table=True):
    id: str = Field(max_length=10, min_length=10, primary_key=True, index=True)
    first_name: str = Field(max_length=25, min_length=1, nullable=False, index=True)
    last_name: str = Field(max_length=25, min_length=1, nullable=False, index=True)
    email: str = Field(max_length=50, nullable=False, unique=True)
    phone: str = Field(max_length=10, min_length=10, nullable=False, unique=True)
    status: PatronStatusEnum = Field(max_length=2, min_length=2, nullable=False, default=PatronStatusEnum.INACTIVE, index=True)
    fine: int = Field(default=0, nullable=False)

    borrows: list["Borrows"] | None = Relationship(back_populates="patron", sa_relationship_kwargs={"cascade": "delete, delete-orphan"})

class Publisher(SQLModel, table=True):
    id: int | None = Field(primary_key=True, index=True, default=None)
    name: str = Field(nullable=False, index=True, max_length=50)
    
    book: list["Book"] | None = Relationship(back_populates="publisher", sa_relationship_kwargs={"cascade": "delete, delete-orphan"})

class Author(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    first_name: str = Field(index=True, max_length=25, nullable=False)
    midname_initial: str = Field(index=True, max_length=25, nullable=False)
    last_name: str = Field(index=True, max_length=25, nullable=False)

    book: list["Book"] | None = Relationship(back_populates="author", sa_relationship_kwargs={"cascade": "delete, delete-orphan"})

class Book(SQLModel, table=True):
    isbn: str = Field(max_length=13, min_length=13, primary_key=True, index=True)
    title: str = Field(max_length=255, min_length=1, nullable=False, index=True)
    genre: str = Field(max_length=25, nullable=False, index=True)
    author_id: int = Field(nullable=False, index=True, foreign_key="author.id")
    publisher_id: int = Field(nullable=False, index=True, foreign_key="publisher.id")
    published_year: int = Field(nullable=False, index=True)
    qty: int = Field(nullable=False, default=1)

    bookcopy: list["BookCopy"] = Relationship(back_populates="book", sa_relationship_kwargs={"cascade": "delete, delete-orphan"})
    author: Author = Relationship(back_populates="book")
    publisher: Publisher = Relationship(back_populates="book")

class BookCopy(SQLModel, table=True):
    id: int | None = Field(primary_key=True, index=True, default=None)
    isbn: str = Field(max_length=13, min_length=13, index=True, foreign_key="book.isbn")

    book: Book = Relationship(back_populates="bookcopy")
    borrows: list["Borrows"] = Relationship(back_populates="bookcopy", sa_relationship_kwargs={"cascade": "delete, delete-orphan"})

class Borrows(SQLModel, table=True):
    id: int | None = Field(primary_key=True, index=True, default=None)
    patron_id: str = Field(max_length=10, min_length=10, nullable=False, index=True, foreign_key="patron.id")
    copy_id: int = Field(nullable=False, index=True, foreign_key="bookcopy.id")
    borrow_date: date = Field(nullable=False, index=True)
    due_date: date = Field(nullable=False, index=True)
    return_date: date = Field(nullable=True, index=True)    

    patron: Patron = Relationship(back_populates="borrows")
    bookcopy: BookCopy = Relationship(back_populates="borrows")