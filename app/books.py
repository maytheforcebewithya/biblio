import streamlit as st
import requests
import pandas as pd
from pydantic import BaseModel, Field, ValidationError
import datetime
import os

API_URL = os.getenv('API_URL', 'http://localhost:8000')

author_url = f"{API_URL}/author"
base_url = f"{API_URL}/book"
publisher_url = f"{API_URL}/publisher"

class CreateBook(BaseModel):
    isbn: str = Field(max_length=13, min_length=10)
    title: str = Field(min_length=10, max_length=255)
    genre: str = Field(min_length=1, max_length=25)
    author_id: int
    publisher_id: int
    published_year: int
    qty: int

class UpdateBook(BaseModel):
    title: str | None = Field(min_length=10, max_length=255, default=None)
    genre: str | None = Field(min_length=1, max_length=25, default=None)
    published_year: int | None = Field(default=None)

def get_authors():
    try:
        response = requests.get(f"{API_URL}/author/all/")
        response.raise_for_status()
        authors = response.json()

        if isinstance(authors, list):
            if authors:
                return {f"{author['first_name']} {author['last_name']}": author['id'] for author in authors}
            else:
                st.warning("No authors added yet.")
                return {}
        elif isinstance(authors, dict) and 'message' in authors:
            st.warning(authors['message'])
            return {}
        else:
            st.error("Unexpected response format from the API.")
            return {}
    except requests.RequestException as e:
        st.error(f"Error fetching authors: {e}")
        return {}

def get_publishers():
    try:
        response = requests.get(f"{API_URL}/publisher/all/")
        response.raise_for_status()
        publishers = response.json()

        if isinstance(publishers, list):
            if publishers:
                return {f"{publisher['name']}": publisher['id'] for publisher in publishers}
            else:
                st.warning("No publishers added yet.")
                return {}
        elif isinstance(publishers, dict) and 'message' in publishers:
            st.warning(publishers['message'])
            return {}
        else:
            st.error("Unexpected response format from the API.")
            return {}
    except requests.RequestException as e:
        st.error(f"Error fetching publishers: {e}")
        return {}

def create_book():
    st.title("Create Book")

    authors = get_authors()  # Fetch authors
    publishers = get_publishers()  # Fetch publishers

    with st.form(key="create_book_form"):
        isbn = st.text_input("ISBN")
        title = st.text_input("Title")
        genre = st.text_input("Genre")
        author_name = st.selectbox("Author", options=list(authors.keys()), index=None)
        publisher_name = st.selectbox("Publisher", options=list(publishers.keys()), index=None)
        published_year = st.number_input("Published Year", min_value=1455, max_value=datetime.datetime.now().year, step=1)
        qty = st.number_input("Quantity", min_value=1, max_value=500, step=1)

        submit_button = st.form_submit_button(label="Create Book")

    if submit_button:
        if not author_name:
            st.error("Please select an author.")
            return
        if not publisher_name:
            st.error("Please select a publisher.")
            return

        try:
            book_data = CreateBook(
                isbn=isbn,
                title=title,
                genre=genre,
                author_id=authors[author_name],
                publisher_id=publishers[publisher_name],
                published_year=published_year,
                qty=qty
            )
            response = requests.post(f"{base_url}/", json=book_data.dict())
            if response.status_code == 200:
                st.success("Book created successfully!")
            else:
                st.error(f"Failed to create book: {response.json().get('detail', 'Unknown error')}")
        except ValidationError as e:
            st.error(f"Validation error: {e}")

def search_book():
    st.title("Search Book")

    show_all = st.checkbox("Show All Books")
    if show_all:
        response = requests.get(f"{base_url}/all")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                df = pd.DataFrame(data)
                desired_order = ['isbn', 'title', 'genre', 'author_id', 'publisher_id', 'published_year', 'qty']
                st.dataframe(df, use_container_width=True, hide_index=True, column_order=desired_order)
            else:
                st.error("Data format is not a list.")
        else:
            st.error(f"Failed to fetch books: {response.json().get('detail', 'Unknown error')}")
    
    else:
        search_type = st.selectbox("Search by:", ["ISBN", "Title", "Genre", "Author", "Publisher"])

        if search_type == "ISBN":
            isbn = st.text_input("Enter ISBN")
            if st.button("Search"):
                response = requests.get(f"{base_url}/isbn/{isbn}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict):
                        df = pd.DataFrame([data])
                        desired_order = ['isbn', 'title', 'genre', 'author_id', 'publisher_id', 'published_year', 'qty']
                        st.dataframe(df, use_container_width=True, hide_index=True, column_order=desired_order)
                    else:
                        st.error("Data format is not a dictionary.")
                else:
                    st.error(f"Failed to fetch book: {response.json().get('detail', 'Unknown error')}")

        elif search_type == "Title":
            title = st.text_input("Enter Book Title")
            if st.button("Search"):
                response = requests.get(f"{base_url}/title/{title}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                        desired_order = ['isbn', 'title', 'genre', 'author_id', 'publisher_id', 'published_year', 'qty']
                        st.dataframe(df, use_container_width=True, hide_index=True, column_order=desired_order)
                    else:
                        st.error("Data format is not a list.")
                else:
                    st.error(f"Failed to fetch books: {response.json().get('detail', 'Unknown error')}")

        elif search_type == "Genre":
            genre = st.text_input("Enter Genre")
            if st.button("Search"):
                response = requests.get(f"{base_url}/genre/{genre}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                        desired_order = ['isbn', 'title', 'genre', 'author_id', 'publisher_id', 'published_year', 'qty']
                        st.dataframe(df, use_container_width=True, hide_index=True, column_order=desired_order)
                    else:
                        st.error("Data format is not a list.")
                else:
                    st.error(f"Failed to fetch books: {response.json().get('detail', 'Unknown error')}")

        elif search_type == "Author":
            author_name = st.text_input("Enter Author Name")
            if st.button("Search"):
                response = requests.get(f"{base_url}/author/{author_name}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                        desired_order = ['isbn', 'title', 'genre', 'author_id', 'publisher_id', 'published_year', 'qty']
                        st.dataframe(df, use_container_width=True, hide_index=True, column_order=desired_order)
                    else:
                        st.error("Data format is not a list.")
                else:
                    st.error(f"Failed to fetch books: {response.json().get('detail', 'Unknown error')}")

        elif search_type == "Publisher":
            publisher_name = st.text_input("Enter Publisher Name")
            if st.button("Search"):
                response = requests.get(f"{base_url}/publisher/{publisher_name}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                        desired_order = ['isbn', 'title', 'genre', 'author_id', 'publisher_id', 'published_year', 'qty']
                        st.dataframe(df, use_container_width=True, hide_index=True, column_order=desired_order)
                    else:
                        st.error("Data format is not a list.")
                else:
                    st.error(f"Failed to fetch books: {response.json().get('detail', 'Unknown error')}")

def update_book():
    st.title("Update Book")

    with st.form(key="update_book_form"):
        isbn = st.text_input("ISBN")
        title = st.text_input("Title", help="Leave blank if not changing")
        genre = st.text_input("Genre", help="Leave blank if not changing")
        published_year = st.number_input("Published Year", min_value=1455, max_value=datetime.datetime.now().year, step=1, help="Leave as 0 if not changing")

        submit_button = st.form_submit_button(label="Update Book")

    if submit_button:
        try:
            book_data = UpdateBook(
                title=title or None,
                genre=genre or None,
                published_year=published_year if published_year != 0 else None
            )
            response = requests.patch(f"{base_url}/{isbn}", json=book_data.dict(exclude_none=True))
            if response.status_code == 200:
                st.success("Book updated successfully!")
            else:
                st.error(f"Failed to update book: {response.json().get('detail', 'Unknown error')}")
        except ValidationError as e:
            st.error(f"Validation error: {e}")

def delete_book():
    st.title("Delete Book")

    with st.form(key="delete_book_form"):
        isbn = st.text_input("ISBN")

        submit_button = st.form_submit_button(label="Delete Book")

    if submit_button:
        response = requests.delete(f"{base_url}/{isbn}")
        if response.status_code == 200:
            st.success("Book deleted successfully!")
        else:
            st.error(f"Failed to delete book: {response.json().get('detail', 'Unknown error')}")

def books_page():
    st.sidebar.title("Book Management")

    options = ["Create Book", "Search Book", "Update Book", "Delete Book"]
    choice = st.sidebar.selectbox("Select Operation", options)

    if choice == "Create Book":
        create_book()
    elif choice == "Search Book":
        search_book()
    elif choice == "Update Book":
        update_book()
    elif choice == "Delete Book":
        delete_book()