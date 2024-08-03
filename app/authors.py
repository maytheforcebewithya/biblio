import streamlit as st
import requests
import pandas as pd
from pydantic import BaseModel, Field, EmailStr, ValidationError
import re
import os

API_URL = os.getenv('API_URL', 'http://localhost:8000')  # Fallback to localhost for local development

base_url = f"{API_URL}/author"

class CreateAuthor(BaseModel):
    author_first_name: str = Field(min_length=1, max_length=25)
    author_initial_midname: str = Field(min_length=1, max_length=25)
    author_last_name: str = Field(min_length=1, max_length=25)

class UpdateAuthor(BaseModel):
    author_first_name: str | None = Field(min_length=1, max_length=25)
    author_initial_midname: str | None = Field(min_length=1, max_length=25)
    author_last_name: str | None = Field(min_length=1, max_length=25)

class DeleteAuthor(BaseModel):
    author_id: int

def create_author():
    st.title("Create Author")

    with st.form(key="create_author_form"):
        first_name = st.text_input("First Name")
        initial_midname = st.text_input("Initial Midname")
        last_name = st.text_input("Last Name")

        submit_button = st.form_submit_button(label="Create Author")

    if submit_button:
        try:
            author_data = CreateAuthor(
                author_first_name=first_name.capitalize(),
                author_initial_midname=initial_midname.capitalize(),
                author_last_name=last_name.capitalize()
            )
            response = requests.post(f"{base_url}/", json=author_data.dict())
            if response.status_code == 200:
                st.success("Author created successfully!")
            else:
                st.error(f"Failed to create author: {response.json().get('detail', 'Unknown error')}")
        except ValidationError as e:
            st.error(f"Validation error: {e}")

def search_author():
    st.title("Search Author")

    show_all = st.checkbox("Show All Authors")
    if show_all:
        response = requests.get(f"{base_url}/all/")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                df = pd.DataFrame(data)
                desired_order = ['id', 'first_name', 'midname_initial' ,'last_name']
                st.dataframe(df, use_container_width=True, hide_index=True, column_order=desired_order)
            else:
                st.error("Data format is not a list.")
        else:
            st.error(f"Failed to fetch authors: {response.json().get('detail', 'Unknown error')}")
    
    else:
        author_name = st.text_input("Enter Author Name")
        if st.button("Search"):
            response = requests.get(f"{base_url}/name/{author_name}/")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    desired_order = ['id', 'first_name', 'midname_initial' ,'last_name']
                    st.dataframe(df, use_container_width=True, hide_index=True, column_order=desired_order)
                else:
                    st.error("Data format is not a list.")
            else:
                st.error(f"Failed to fetch authors: {response.json().get('detail', 'Unknown error')}")

def update_author():
    st.title("Update Author")

    with st.form(key="update_author_form"):
        author_id = st.text_input("Author ID")
        first_name = st.text_input("First Name", help="Leave blank if not changing")
        initial_midname = st.text_input("Initial Midname", help="Leave blank if not changing")
        last_name = st.text_input("Last Name", help="Leave blank if not changing")

        submit_button = st.form_submit_button(label="Update Author")

    if submit_button:
        try:
            author_data = UpdateAuthor(
                author_first_name=first_name.capitalize() or None,
                author_initial_midname=initial_midname.capitalize() or None,
                author_last_name=last_name.capitalize() or None
            )
            response = requests.patch(f"{base_url}/{author_id}", json=author_data.dict(exclude_unset=True))
            if response.status_code == 200:
                st.success("Author updated successfully!")
            else:
                st.error(f"Failed to update author: {response.json().get('detail', 'Unknown error')}")
        except ValidationError as e:
            st.error(f"Validation error: {e}")

def delete_author():
    st.title("Delete Author")

    with st.form(key="delete_author_form"):
        author_id = st.text_input("Author ID")

        submit_button = st.form_submit_button(label="Delete Author")

    if submit_button:
        try:
            author_data = DeleteAuthor(author_id=author_id)
            response = requests.delete(f"{base_url}/{author_id}/")
            if response.status_code == 200:
                st.success("Author deleted successfully!")
            else:
                st.error(f"Failed to delete author: {response.json().get('detail', 'Unknown error')}")
        except ValidationError as e:
            st.error(f"Validation error: {e}")

def authors_page():
    st.sidebar.title("Author Management")

    options = ["Create Author", "Search Author", "Update Author", "Delete Author"]
    choice = st.sidebar.selectbox("Select Operation", options)

    if choice == "Create Author":
        create_author()
    elif choice == "Search Author":
        search_author()
    elif choice == "Update Author":
        update_author()
    elif choice == "Delete Author":
        delete_author()

