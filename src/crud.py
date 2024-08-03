from database import engine
from datetime import timedelta, datetime, date
from fastapi import HTTPException, Depends
from models import PatronStatusEnum, Patron, Publisher, Author, Book, BookCopy, Borrows
from schemas import CreatePatron, ReadPatron, ReadPatronByFine, UpdatePatron, DeletePatron, CreateBook, ReadBook, ReadBookByTitle, UpdateBook, DeleteBook, CreateAuthor, UpdateAuthor, DeleteAuthor, CreatePublisher, UpdatePublisher, DeletePublisher, AddBorrow, ReturnBorrow
from sqlmodel import Session, select, func, join
from exceptions import NotFoundException, InvalidRequestException, DuplicateEntryException, DBIntegrityError
from sqlalchemy.exc import IntegrityError, DatabaseError
from exconstants import *


def get_session():
    return Session(engine)

# Patron CRUD
def get_all_patrons(session: Session = Depends(get_session)):
    try:
        operation = select(Patron)
        patrons = session.exec(operation).all()
        if not patrons:
            return {
                "message": "No patrons added yet."
            }
        return patrons
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def create_patron(body: CreatePatron, session: Session = Depends(get_session)):
    try:
        duplicate_id = session.exec(select(Patron).where(Patron.id == body.patron_id)).one_or_none()
        if duplicate_id:
            raise DuplicateEntryException(detail=DUPLICATE_PATRON_ID)
        duplicate_email = session.exec(select(Patron).where(Patron.email == body.patron_email)).one_or_none()
        if duplicate_email:
            raise DuplicateEntryException(detail=DUPLICATE_PATRON_EMAIL)
        duplicate_phone = session.exec(select(Patron).where(Patron.phone == body.patron_phone)).one_or_none()
        if duplicate_phone:
            raise DuplicateEntryException(detail=DUPLICATE_PATRON_PHONE)
        patron = Patron(
            id = body.patron_id,
            first_name = body.patron_first_name,
            last_name = body.patron_last_name,
            email = body.patron_email,
            phone = body.patron_phone,
            status = PatronStatusEnum.INACTIVE
        )
        session.add(patron)
        session.commit()
        session.refresh(patron)
        return patron
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def get_patron_by_id(body: ReadPatron, session: Session = Depends(get_session)):
    try:
        operation = select(Patron).where(Patron.id == body.patron_id)
        patron = session.exec(operation).first()
        if not patron:
            raise NotFoundException(detail=PATRON_NOT_FOUND)
        return patron
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def get_patron_by_name(patron_name: str, session: Session = Depends(get_session)):
    try:
        parts = patron_name.split()    
        if len(parts) != 2:
            raise InvalidRequestException(detail=PATRON_NAME_INVALID)    
        first_name = parts[0]
        last_name = parts[1] 
        operation = select(Patron).where(Patron.first_name == first_name).where(Patron.last_name == last_name).limit(3)
        patrons = session.execute(operation).all()
        if not patrons:
            raise NotFoundException(detail=PATRON_NOT_FOUND)
        patrons = [patron[0] for patron in patrons]    
        return patrons 
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def get_patron_by_fine(body: ReadPatronByFine, session: Session = Depends(get_session)):
    try:
        operation = select(Patron).where(Patron.fine > body.patron_fine).limit(10)
        patrons = session.exec(operation).all()
        if not patrons:
            raise NotFoundException(detail=PATRON_NOT_FOUND)
        return patrons
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def update_patron(body: UpdatePatron, patron_id: str, session: Session = Depends(get_session)):
    try:
        operation = select(Patron).where(Patron.id == patron_id)
        patron = session.exec(operation).one_or_none()
        if not patron:
            raise NotFoundException(detail=PATRON_NOT_FOUND)
        if body.patron_first_name is not None:
            patron.first_name = body.patron_first_name
        if body.patron_last_name is not None:
            patron.last_name = body.patron_last_name
        if body.patron_email is not None:
            patron.email = body.patron_email
        if body.patron_phone is not None:
            patron.phone = body.patron_phone
        session.add(patron)
        session.commit()
        session.refresh(patron)  
        return patron      
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError
        
def delete_patron(patron_id: str, session: Session = Depends(get_session)):
    try:
        operation = select(Patron).where(Patron.id == patron_id)
        patron = session.exec(operation).one_or_none()
        if not patron:
            raise NotFoundException(detail=PATRON_NOT_FOUND)
        session.delete(patron)   
        session.commit()
        return {
            "message": "Patron deleted successfully"
        }
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

# Book CRUD
def get_all_books(session: Session = Depends(get_session)):
    try:
        operation = select(Book)
        books = session.exec(operation).all()
        if not books:
            return {
                "message": "No books added yet."
            }
        return books
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def create_book(body: CreateBook, session: Session = Depends(get_session)):
    try:
        duplicate_isbn = session.exec(select(Book).where(Book.isbn == body.isbn)).one_or_none()
        if duplicate_isbn:
            raise NotFoundException(detail=BOOK_NOT_FOUND)
        book = Book(
            isbn = body.isbn,
            title = body.title,
            genre = body.genre,
            author_id = body.author_id,
            publisher_id = body.publisher_id,
            published_year = body.published_year,
            qty = body.qty
        )
        session.add(book)
        book_copies = [BookCopy(isbn=body.isbn) for _ in range(body.qty)]
        session.bulk_save_objects(book_copies)
        session.commit()
        session.refresh(book)
        return book
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def get_book_by_isbn(body: ReadBook, session: Session = Depends(get_session)):
    try:
        operation = select(Book).where(Book.isbn == body.isbn)
        book = session.exec(operation).one_or_none()
        if not book:
            raise NotFoundException(detail=BOOK_NOT_FOUND)
        return book
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def get_book_by_title(body: ReadBookByTitle, session: Session = Depends(get_session)):
    try:
        operation = select(Book).where(Book.title == body.title).limit(3)
        books = session.exec(operation).all()
        if not books:
            raise NotFoundException(detail=BOOK_NOT_FOUND)
        return books
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def get_book_by_author(author_name: str, session: Session = Depends(get_session)):
    try:
        parts = author_name.split()
        first_name = parts[0]
        midname_initial = parts[1]
        last_name = parts[2]
        operation = select(Book).join(Author).where(
            Author.first_name == first_name,
            Author.midname_initial == midname_initial,
            Author.last_name == last_name
        ).limit(3)
        books = session.execute(operation).all()
        if not books:
            raise NotFoundException(detail=BOOK_NOT_FOUND)
        books = [book[0] for book in books]
        return books
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def get_book_by_publisher(publisher_name: str, session: Session):
    try:
        operation = select(Book).join(Publisher).where(
            Publisher.name == publisher_name
        ).limit(3)
        books = session.execute(operation).all()
        if not books:
            raise NotFoundException(detail=BOOK_NOT_FOUND)
        books = [book[0] for book in books]
        return books
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def get_book_by_genre(genre: str, session: Session):
    try:
        operation = select(Book).where(
            Book.genre == genre
        ).limit(3)
        books = session.execute(operation).all()
        if not books:
            raise NotFoundException(detail=BOOK_NOT_FOUND)
        books = [book[0] for book in books]
        return books
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def update_book(body: UpdateBook, isbn: ReadBook, session: Session = Depends(get_session)):
    try:
        operation = select(Book).where(Book.isbn == isbn.isbn)
        book = session.exec(operation).one_or_none()
        if not book:
            raise NotFoundException(detail=BOOK_NOT_FOUND)
        if body.title is not None:
            book.title = body.title
        if body.genre is not None:
            book.genre = body.genre
        if body.published_year is not None:
            book.published_year = body.published_year
        session.add(book)
        session.commit()
        session.refresh(book)
        return book
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def delete_book(isbn: str, session: Session = Depends(get_session)):
    try:
        operation = select(Book).where(Book.isbn == isbn)
        book = session.exec(operation).one_or_none()
        if not book:
            raise NotFoundException(detail=BOOK_NOT_FOUND)
        session.delete(book)   
        session.commit()
        return {
            "message": "Book deleted successfully"
        }
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

# Author CRUD
def get_all_authors(session: Session = Depends(get_session)):
    try:
        operation = select(Author)
        authors = session.exec(operation).all()
        if not authors:
            return []
        return authors
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def create_author(body: CreateAuthor, session: Session = Depends(get_session)):
    try:        
        duplicate_author = session.exec(select(Author).where(Author.first_name == body.author_first_name).where(Author.midname_initial == body.author_initial_midname).where(Author.last_name == body.author_last_name)).one_or_none()
        if duplicate_author:
            raise DuplicateEntryException(detail=DUPLICATE_AUTHOR)
        author = Author(
            first_name = body.author_first_name,
            midname_initial = body.author_initial_midname,
            last_name = body.author_last_name
        )
        session.add(author)
        session.commit()
        session.refresh(author)
        return author
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError
        
def get_author_by_name(author_name: str, session: Session):
    try:
        parts = author_name.split()    
        if len(parts) != 3:
            raise InvalidRequestException(detail=AUTHOR_NAME_INVALID) 
        first_name = parts[0]
        midname_initial = parts[1]
        last_name = parts[2]    
        operation = select(Author).where(
            Author.first_name == first_name,
            Author.midname_initial == midname_initial,
            Author.last_name == last_name
        ).limit(3)    
        authors = session.execute(operation).all()    
        if not authors:
            raise NotFoundException(detail=AUTHOR_NOT_FOUND)   
        authors = [author[0] for author in authors]    
        return authors
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def update_author(body: UpdateAuthor, author_id: int, session: Session = Depends(get_session)):
    try:
        operation = select(Author).where(Author.id == author_id)
        author = session.exec(operation).one_or_none()
        if not author:
            raise NotFoundException(detail=AUTHOR_NOT_FOUND)   
        if body.author_first_name is not None:
            author.first_name = body.author_first_name
        if body.author_initial_midname is not None:
            author.midname_initial = body.author_initial_midname
        if body.author_last_name is not None:
            author.last_name = body.author_last_name
        session.add(author)
        session.commit()
        session.refresh(author)
        return author
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def delete_author(author_id: int, session: Session = Depends(get_session)):
    try:
        operation = select(Author).where(Author.id == author_id)
        author = session.exec(operation).one_or_none()
        if not author:
            raise NotFoundException(detail=AUTHOR_NOT_FOUND)   
        session.delete(author)   
        session.commit()
        return {
            "message": "Book deleted successfully"
        }
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

# Publisher CRUD
def get_all_publishers(session: Session = Depends(get_session)):
    try:
        operation = select(Publisher)
        publishers = session.exec(operation).all()
        if not publishers:
            return {
                "message": "No publishers added yet."
            }
        return publishers
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def create_publisher(body: CreatePublisher, session: Session = Depends(get_session)):
    try:
        duplicate_publisher = session.exec(select(Publisher).where(Publisher.name == body.publisher_name)).one_or_none()
        if duplicate_publisher:
            raise DuplicateEntryException(detail=DUPLICATE_PUBLISHER)
        publisher = Publisher(
            name = body.publisher_name
        )
        session.add(publisher)
        session.commit()
        session.refresh(publisher)
        return publisher
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def update_publisher(body: UpdatePublisher, publisher_id: int, session: Session = Depends(get_session)):
    try:
        operation = select(Publisher).where(Publisher.id == publisher_id)
        publisher = session.exec(operation).one_or_none()
        if not publisher:
            raise NotFoundException(detail=PUBLISHER_NOT_FOUND)
        if body.publisher_name is not None:
            publisher.name = body.publisher_name
        session.add(publisher)
        session.commit()
        session.refresh(publisher)
        return publisher
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def get_publisher_by_name(publisher_name: str, session: Session = Depends(get_session)):
    try:
        operation = select(Publisher).where(Publisher.name == publisher_name).limit(3)
        publishers = session.execute(operation).all()
        if not publishers:
            raise NotFoundException(detail=PUBLISHER_NOT_FOUND)
        publishers = [publisher[0] for publisher in publishers]    
        return publishers    
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError   

def delete_publisher(publisher_id: int, session: Session = Depends(get_session)):
    try:
        operation = select(Publisher).where(Publisher.id == publisher_id)
        publisher = session.exec(operation).one_or_none()
        if not publisher:
            raise NotFoundException(detail=PUBLISHER_NOT_FOUND)
        session.delete(publisher)   
        session.commit()
        return {
            "message": "Publisher deleted successfully"
        }
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

# Bookcopy CRUD
def get_available_bookcopies(session: Session = Depends(get_session)):
    try:
        borrowed_copies_subquery = select(Borrows.copy_id).where(Borrows.return_date.is_(None)).subquery()
        operation = (
            select(BookCopy, Book, Author, Publisher)
            .join(Book, BookCopy.isbn == Book.isbn)
            .join(Author, Book.author_id == Author.id)
            .join(Publisher, Book.publisher_id == Publisher.id)
            .where(BookCopy.id.not_in(borrowed_copies_subquery))
        )
        result = session.exec(operation).all()
        if not result:
            return []
        
        available_bookcopies = [
            {
                "id": bookcopy.id,
                "isbn": bookcopy.isbn,
                "title": book.title,
                "author": f"{author.first_name} {author.midname_initial} {author.last_name}",
                "publisher": publisher.name
            }
            for bookcopy, book, author, publisher in result
        ]
        return available_bookcopies
    except IntegrityError:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError:
        session.rollback()
        raise DatabaseError

def get_overdue_bookcopies(session: Session = Depends(get_session)):
    try:
        today = date.today()
        operation = (
            select(Borrows, BookCopy, Book, Author, Publisher)
            .join(BookCopy, Borrows.copy_id == BookCopy.id)
            .join(Book, BookCopy.isbn == Book.isbn)
            .join(Author, Book.author_id == Author.id)
            .join(Publisher, Book.publisher_id == Publisher.id)
            .where(Borrows.due_date < today)
            .where(Borrows.return_date == None)
        )
        result = session.exec(operation).all()
        if not result:
            return []
        overdue_bookcopies = [
            {
                "borrow_id": borrow.id,
                "patron_id": borrow.patron_id,
                "due_date": borrow.due_date,
                "borrow_date": borrow.borrow_date,
                "return_date": borrow.return_date,
                "copy_id": bookcopy.id,
                "isbn": book.isbn,
                "title": book.title,
                "author": f"{author.first_name} {author.midname_initial} {author.last_name}",
                "publisher": publisher.name
            }
            for borrow, bookcopy, book, author, publisher in result
        ]
        return overdue_bookcopies
    except IntegrityError:
        session.rollback()
        raise DBIntegrityError
    except SQLAlchemyDatabaseError:
        session.rollback()
        raise DatabaseError

# Borrow CRUD
def get_all_borrows(session: Session = Depends(get_session)):
    try:
        operation = (
            select(Borrows, BookCopy, Book, Author, Publisher)
            .join(BookCopy, Borrows.copy_id == BookCopy.id)
            .join(Book, BookCopy.isbn == Book.isbn)
            .join(Author, Book.author_id == Author.id)
            .join(Publisher, Book.publisher_id == Publisher.id)
        )
        result = session.exec(operation).all()
        if not result:
            return {
                "message": "No borrows transacted yet."
            }
        borrows = [
            {
                "borrow_id": borrow.id,
                "patron_id": borrow.patron_id,
                "due_date": borrow.due_date,
                "borrow_date": borrow.borrow_date,
                "return_date": borrow.return_date,
                "copy_id": bookcopy.id,
                "isbn": book.isbn,
                "title": book.title,
                "author": f"{author.first_name} {author.midname_initial} {author.last_name}",
                "publisher": publisher.name
            }
            for borrow, bookcopy, book, author, publisher in result
        ]
        return borrows
    except IntegrityError:
        session.rollback()
        raise DBIntegrityError
    except SQLAlchemyDatabaseError:
        session.rollback()
        raise DatabaseError

def create_borrow(body: AddBorrow, session: Session = Depends(get_session)):
    try:
        book_copy = session.exec(select(BookCopy).where(BookCopy.id == body.copy_id)).one_or_none()
        if not book_copy:
            raise NotFoundException(detail="Book copy not found")
        
        book = session.exec(select(Book).where(Book.isbn == book_copy.isbn)).one_or_none()
        if not book:
            raise NotFoundException(detail="Associated book not found")
        existing_borrow = session.exec(select(Borrows).where(Borrows.copy_id == body.copy_id).where(Borrows.return_date == None)).one_or_none()
        if existing_borrow:
            raise DuplicateEntryException(detail=DUPLICATE_BORROW)
        duplicate_borrow = session.exec(select(Borrows).where(Borrows.patron_id == body.patron_id).where(Borrows.copy_id == body.copy_id).where(Borrows.borrow_date == body.borrow_date)).one_or_none()
        if duplicate_borrow:
            raise DuplicateEntryException(detail="This book has already been borrowed")
        borrow = Borrows(
            patron_id=body.patron_id,
            copy_id=body.copy_id,
            borrow_date=body.borrow_date,
            due_date=body.borrow_date + timedelta(days=15),
            return_date=None
        )

        patron = session.exec(select(Patron).where(Patron.id == body.patron_id)).one_or_none()
        if not patron:
            raise NotFoundException(detail="Patron not found")
        if patron.status != PatronStatusEnum.ACTIVE:
            patron.status = PatronStatusEnum.ACTIVE

        session.add(borrow)
        session.commit()
        session.refresh(borrow)
        return borrow

    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def return_borrow(transaction_id: int, body: ReturnBorrow, session: Session = Depends(get_session)):
    try:
        operation = select(Borrows).where(Borrows.id == transaction_id)
        transaction = session.exec(operation).one_or_none()
        if not transaction:
            raise NotFoundException(detail=BORROW_NOT_FOUND)
        transaction.return_date = body.return_date
        session.add(transaction)
        session.commit()
        patron = session.exec(select(Patron).where(Patron.id == transaction.patron_id)).one_or_none()
        patron_activity = False       
        for borrow in patron.borrows:
            if not borrow.return_date:
                patron_activity = True
        if patron_activity == False:
            patron.status = PatronStatusEnum.INACTIVE
        session.add(patron)
        session.commit()
        session.refresh(patron)
        return {
            "message": "Borrow returned successfully"
        }
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def get_borrows_by_patron(patron_id: str, session: Session = Depends(get_session)):
    try:
        operation = (
            select(Borrows, BookCopy, Book, Author, Publisher)
            .join(BookCopy, Borrows.copy_id == BookCopy.id)
            .join(Book, BookCopy.isbn == Book.isbn)
            .join(Author, Book.author_id == Author.id)
            .join(Publisher, Book.publisher_id == Publisher.id)
            .where(Borrows.patron_id == patron_id)
        )
        result = session.exec(operation).all()
        if not result:
            return {
                "message": "No borrows found for this patron."
            }
        borrows = [
            {
                "borrow_id": borrow.id,
                "patron_id": borrow.patron_id,
                "due_date": borrow.due_date,
                "borrow_date": borrow.borrow_date,
                "return_date": borrow.return_date,
                "copy_id": bookcopy.id,
                "isbn": book.isbn,
                "title": book.title,
                "author": f"{author.first_name} {author.midname_initial} {author.last_name}",
                "publisher": publisher.name
            }
            for borrow, bookcopy, book, author, publisher in result
        ]
        return borrows
    except IntegrityError:
        session.rollback()
        raise DBIntegrityError
    except SQLAlchemyDatabaseError:
        session.rollback()
        raise DatabaseError

def get_borrows_by_isbn(isbn: str, session: Session = Depends(get_session)):
    try:
        operation = (
            select(Borrows, BookCopy, Book, Author, Publisher)
            .join(BookCopy, Borrows.copy_id == BookCopy.id)
            .join(Book, BookCopy.isbn == Book.isbn)
            .join(Author, Book.author_id == Author.id)
            .join(Publisher, Book.publisher_id == Publisher.id)
            .where(BookCopy.isbn == isbn)
        )
        result = session.exec(operation).all()
        if not result:
            return {
                "message": "No borrows found for this ISBN."
            }
        borrows = [
            {
                "borrow_id": borrow.id,
                "patron_id": borrow.patron_id,
                "due_date": borrow.due_date,
                "borrow_date": borrow.borrow_date,
                "return_date": borrow.return_date,
                "copy_id": bookcopy.id,
                "isbn": book.isbn,
                "title": book.title,
                "author": f"{author.first_name} {author.midname_initial} {author.last_name}",
                "publisher": publisher.name
            }
            for borrow, bookcopy, book, author, publisher in result
        ]
        return borrows
    except IntegrityError:
        session.rollback()
        raise DBIntegrityError
    except SQLAlchemyDatabaseError:
        session.rollback()
        raise DatabaseError

# worker functions
def get_due_books(session: Session = Depends(get_session)):
    try:
        today = date.today()
        operation = select(Borrows).where(Borrows.due_date < today).where(Borrows.return_date == None)
        due_books = session.exec(operation).all()
        if not due_books:
            return []
        return due_books
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def calculate_patron_fines(session: Session = Depends(get_session)):
    try:
        today = date.today()
        operation = select(Borrows).where(Borrows.due_date < today).where(Borrows.return_date == None)
        overdue_books = session.exec(operation).all()
        for book in overdue_books:
            patron = session.exec(select(Patron).where(Patron.id == book.patron_id)).one()
            patron.fine += 1
            session.add(patron)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

# aggregate functions
def count_patrons(session: Session = Depends(get_session)):
    try:
        count = session.execute(select(func.count(Patron.id))).scalar()
        return count
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def count_authors(session: Session = Depends(get_session)):
    try:
        count = session.execute(select(func.count(Author.id))).scalar()
        return count
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def count_publishers(session: Session = Depends(get_session)):
    try:
        count = session.execute(select(func.count(Publisher.id))).scalar()
        return count
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def count_books(session: Session = Depends(get_session)):
    try:
        count = session.execute(select(func.count(Book.isbn))).scalar()
        return count
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def count_bookcopies(session: Session = Depends(get_session)):
    try:
        count = session.execute(select(func.count(BookCopy.id))).scalar()
        return count
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def count_transactions(session: Session = Depends(get_session)):
    try:
        count = session.execute(select(func.count(Borrows.id))).scalar()
        return count
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def count_unreturned_bookcopies(session: Session = Depends(get_session)):
    try:
        count = session.execute(select(func.count(Borrows.id)).where(Borrows.return_date == None)).scalar()
        return count
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError

def sum_of_patron_fines(session: Session = Depends(get_session)):
    try:
        fine_total = session.execute(select(func.sum(Patron.fine))).scalar()
        return fine_total
    except IntegrityError as e:
        session.rollback()
        raise DBIntegrityError
    except DatabaseError as e:
        session.rollback()
        raise DatabaseError 