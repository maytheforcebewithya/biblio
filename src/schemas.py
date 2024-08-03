from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError, ValidationInfo
import re
import datetime

class CreatePatron(BaseModel):
    patron_id: str = Field(min_length=10, max_length=10)
    patron_first_name: str = Field(min_length=1, max_length=25)
    patron_last_name: str = Field(min_length=1, max_length=25)
    patron_email: EmailStr = Field(max_length=50)
    patron_phone: str = Field(min_length=10, max_length=10)

    @field_validator('patron_id', mode='before')
    def validate_patron_id(cls, value: str):
        value = value.strip()
        pattern = r'^1MS\d{2}(EC|CS|ME|EE|CE|IM|CH|MD|IS|BT|IE|EI|ET|AI|AD|CY|CA)\d{3}$'
        if not re.match(pattern, value):
            raise ValueError('Invalid patron_id format')
        year_of_admission = int(value[3:5])        
        current_year = datetime.datetime.now().year % 100
        if year_of_admission > current_year:
            raise ValueError('Invalid year of admission')        
        return value

    @field_validator('patron_phone', mode='before')
    def validate_patron_phone(cls, value: str):
        pattern = r'^\d{10}$'
        value = value.strip()
        if not re.match(pattern, value):
            raise ValueError('Invalid patron_phone format')        
        return value   

class ReadPatron(BaseModel):
    patron_id: str = Field(min_length=10, max_length=10)

    @field_validator('patron_id', mode='before')
    def validate_patron_id(cls, value: str):
        value = value.strip()
        pattern = r'^1MS\d{2}(EC|CS|ME|EE|CE|IM|CH|MD|IS|BT|IE|EI|ET|AI|AD|CY|CA)\d{3}$'
        if not re.match(pattern, value):
            raise ValueError('Invalid patron_id format')
        year_of_admission = int(value[3:5])        
        current_year = datetime.datetime.now().year % 100
        if year_of_admission > current_year:
            raise ValueError('Invalid year of admission')        
        return value

class ReadPatronByFine(BaseModel):
    patron_fine: int | None

class UpdatePatron(BaseModel):
    patron_first_name: str | None = Field(min_length=1, max_length=25, default=None)
    patron_last_name: str | None = Field(min_length=1, max_length=25, default=None)
    patron_email: EmailStr | None = Field(max_length=50, default=None)
    patron_phone: str | None = Field(min_length=10, max_length=10, default=None)
    
    @field_validator('patron_phone', mode='before')
    def validate_patron_phone(cls, value: str):
        if value is not None:
            pattern = r'^\d{10}$'
            value = value.strip()
            if not re.match(pattern, value):
                raise ValueError('Invalid patron_phone format')        
            return value

class DeletePatron(BaseModel):
    patron_id: str = Field(min_length=10, max_length=10)

    @field_validator('patron_id', mode='before')
    def validate_patron_id(cls, value: str):
        value = value.strip()
        pattern = r'^1MS\d{2}(EC|CS|ME|EE|CE|IM|CH|MD|IS|BT|IE|EI|ET|AI|AD|CY|CA)\d{3}$'
        if not re.match(pattern, value):
            raise ValueError('Invalid patron_id format')
        year_of_admission = int(value[3:5])        
        current_year = datetime.datetime.now().year % 100
        if year_of_admission > current_year:
            raise ValueError('Invalid year of admission')        
        return value

class CreateBook(BaseModel):
    isbn: str = Field(max_length=13, min_length=10)
    title: str = Field(min_length=10, max_length=255)
    genre: str = Field(min_length=1, max_length=25)
    author_id: int
    publisher_id: int
    published_year: int
    qty: int

    @field_validator('isbn', mode='before')
    def validate_isbn(cls, value: str):
        value = value.strip()
        if not value[:-1].isdigit() or (value[-1] not in "0123456789Xx"):
            raise ValueError("ISBN must only contain numeric characters or 'X' for ISBN-10.")        
        if len(value) != 10 and len(value) != 13:
            raise ValueError("ISBN must be 10 or 13 characters long.")        
        if len(value) == 10:
            w_sum = 0
            for i in range(9):
                w_sum += (10 - i) * int(value[i])            
            check_digit = value[9].upper()
            w_sum += 10 if check_digit == 'X' else int(check_digit)            
            if w_sum % 11 != 0:
                raise ValueError("Invalid ISBN-10")
            else:
                value = '978' + value[:-1]
                w_sum = 0
                for i in range(12):
                    w_sum += int(value[i]) * (1 if i % 2 == 0 else 3)
                check_digit = (10 - (w_sum % 10)) % 10
                value += str(check_digit)
                return value
        elif len(value) == 13:
            w_sum = 0
            for i in range(12):
                w_sum += int(value[i]) * (1 if i % 2 == 0 else 3)
            check_digit = int(value[12])            
            if (10 - (w_sum % 10)) % 10 != check_digit:
                raise ValueError("Invalid ISBN-13")
            else:
                return value

    @field_validator('qty', mode='before')
    def validate_qty(cls, value: int):
        if value > 500 or value < 1:
            raise ValueError('Order cannot have more than a 500 copies of a book, and orders cannot be of zero quantity')
        return value

    @field_validator('published_year', mode='before')
    def validate_published_year(cls, value: int):
        current_year = datetime.datetime.now().year
        if value < 1455 or value > current_year:
            raise ValueError(f'Published year must be between 1455 and {current_year}')
        return value

class ReadBook(BaseModel):
    isbn: str | None = Field(max_length=13, min_length=10)

    @field_validator('isbn', mode='before')
    def validate_isbn(cls, value: str):
        if value is not None:
            value = value.replace("-", "")
            value = value.strip()
            if not value[:-1].isdigit() or (value[-1] not in "0123456789Xx"):
                raise ValueError("ISBN must only contain numeric characters or 'X' for ISBN-10.")        
            if len(value) != 10 and len(value) != 13:
                raise ValueError("ISBN must be 10 or 13 characters long.")        
            if len(value) == 10:
                w_sum = 0
                for i in range(9):
                    w_sum += (10 - i) * int(value[i])            
                check_digit = value[9].upper()
                w_sum += 10 if check_digit == 'X' else int(check_digit)            
                if w_sum % 11 != 0:
                    raise ValueError("Invalid ISBN-10")
                else:
                    value = '978' + value[:-1]
                    w_sum = 0
                    for i in range(12):
                        w_sum += int(value[i]) * (1 if i % 2 == 0 else 3)
                    check_digit = (10 - (w_sum % 10)) % 10
                    value += str(check_digit)
                    return value
            elif len(value) == 13:
                w_sum = 0
                for i in range(12):
                    w_sum += int(value[i]) * (1 if i % 2 == 0 else 3)
                check_digit = int(value[12])            
                if (10 - (w_sum % 10)) % 10 != check_digit:
                    raise ValueError("Invalid ISBN-13")
                else:
                    return value

class ReadBookByTitle(BaseModel):
    title: str | None = Field(min_length=10, max_length=255)

class UpdateBook(BaseModel):
    title: str | None = Field(min_length=10, max_length=255, default=None)
    genre: str | None = Field(min_length=1, max_length=25, default=None)
    published_year: int | None = Field(default=None)

    @field_validator('published_year', mode='before')
    def validate_published_year(cls, value: int):
        if value is not None:
            current_year = datetime.datetime.now().year
            if value < 1455 or value > current_year:
                raise ValueError(f'Published year must be between 1455 and {current_year}')
            return value

class DeleteBook(BaseModel):
    isbn: str = Field(max_length=20, min_length=10)  

    @field_validator('isbn', mode='before')
    def validate_isbn(cls, value: str):
        value = value.replace("-", "")
        value = value.strip()
        if not value[:-1].isdigit() or (value[-1] not in "0123456789Xx"):
            raise ValueError("ISBN must only contain numeric characters or 'X' for ISBN-10.")        
        if len(value) != 10 and len(value) != 13:
            raise ValueError("ISBN must be 10 or 13 characters long.")        
        if len(value) == 10:
            w_sum = 0
            for i in range(9):
                w_sum += (10 - i) * int(value[i])            
            check_digit = value[9].upper()
            w_sum += 10 if check_digit == 'X' else int(check_digit)            
            if w_sum % 11 != 0:
                raise ValueError("Invalid ISBN-10")
            else:
                value = '978' + value[:-1]
                w_sum = 0
                for i in range(12):
                    w_sum += int(value[i]) * (1 if i % 2 == 0 else 3)
                check_digit = (10 - (w_sum % 10)) % 10
                value += str(check_digit)
                return value

        elif len(value) == 13:
            w_sum = 0
            for i in range(12):
                w_sum += int(value[i]) * (1 if i % 2 == 0 else 3)
            check_digit = int(value[12])            
            if (10 - (w_sum % 10)) % 10 != check_digit:
                raise ValueError("Invalid ISBN-13")
            else:
                return value

class CreateAuthor(BaseModel):
    author_first_name: str = Field(min_length=1, max_length=25)
    author_initial_midname: str = Field(min_length=1, max_length=25)
    author_last_name: str = Field(min_length=1, max_length=25)

class UpdateAuthor(BaseModel):
    author_first_name: str | None = Field(min_length=1, max_length=25, default=None)
    author_initial_midname: str | None = Field(min_length=1, max_length=25, default=None)
    author_last_name: str | None = Field(min_length=1, max_length=25, default=None)

class DeleteAuthor(BaseModel):
    author_id: int

class CreatePublisher(BaseModel):
    publisher_name: str = Field(min_length=1, max_length=50)

class UpdatePublisher(BaseModel):
    publisher_name: str | None = Field(min_length=1, max_length=50, default=None)

class DeletePublisher(BaseModel):
    publisher_id: int

class AddBorrow(BaseModel):
    patron_id: str
    copy_id: int
    borrow_date: datetime.date

    @field_validator('patron_id', mode='before')
    def validate_patron_id(cls, value: str):
        value = value.strip()
        pattern = r'^1MS\d{2}(EC|CS|ME|EE|CE|IM|CH|MD|IS|BT|IE|EI|ET|AI|AD|CY|CA)\d{3}$'
        if not re.match(pattern, value):
            raise ValueError('Invalid patron_id format')
        year_of_admission = int(value[3:5])        
        current_year = datetime.datetime.now().year % 100
        if year_of_admission > current_year:
            raise ValueError('Invalid year of admission')        
        return value

class ReturnBorrow(BaseModel):
    return_date: datetime.date