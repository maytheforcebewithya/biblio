import streamlit as st
import requests
import pandas as pd
from pydantic import BaseModel, Field, ValidationError
import os

API_URL = os.getenv('API_URL', 'http://localhost:8000')

base_url = f"{API_URL}/publisher"

class CreatePublisher(BaseModel):
    publisher_name: str = Field(min_length=1, max_length=50)

class UpdatePublisher(BaseModel):
    publisher_name: str = Field(min_length=1, max_length=50)

class DeletePublisher(BaseModel):
    publisher_id: int

def create_publisher():
    st.title("Create Publisher")

    with st.form(key="create_publisher_form"):
        publisher_name = st.text_input("Publisher Name")

        submit_button = st.form_submit_button(label="Create Publisher")

    if submit_button:
        try:
            publisher_data = CreatePublisher(publisher_name=publisher_name)
            response = requests.post(f"{base_url}/", json=publisher_data.dict())
            if response.status_code == 200:
                st.success("Publisher created successfully!")
            else:
                st.error(f"Failed to create publisher: {response.json().get('detail', 'Unknown error')}")
        except ValidationError as e:
            st.error(f"Validation error: {e}")

def search_publisher():
    st.title("Search Publisher")

    show_all = st.checkbox("Show All Publishers")
    if show_all:
        response = requests.get(f"{base_url}/all/")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.error("Data format is not a list.")
        else:
            st.error(f"Failed to fetch publishers: {response.json().get('detail', 'Unknown error')}")
    else:
        publisher_name = st.text_input("Enter Publisher Name")
        if st.button("Search"):
            response = requests.get(f"{base_url}/name/{publisher_name}/")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.error("Data format is not a list.")
            else:
                st.error(f"Failed to fetch publishers: {response.json().get('detail', 'Unknown error')}")

def update_publisher():
    st.title("Update Publisher")

    with st.form(key="update_publisher_form"):
        publisher_id = st.text_input("Publisher ID")
        publisher_name = st.text_input("Publisher Name", help="Leave blank if not changing")

        submit_button = st.form_submit_button(label="Update Publisher")

    if submit_button:
        try:
            publisher_data = UpdatePublisher(publisher_name=publisher_name or None)
            response = requests.patch(f"{base_url}/{publisher_id}", json=publisher_data.dict(exclude_unset=True))
            if response.status_code == 200:
                st.success("Publisher updated successfully!")
            else:
                st.error(f"Failed to update publisher: {response.json().get('detail', 'Unknown error')}")
        except ValidationError as e:
            st.error(f"Validation error: {e}")

def delete_publisher():
    st.title("Delete Publisher")

    with st.form(key="delete_publisher_form"):
        publisher_id = st.text_input("Publisher ID")

        submit_button = st.form_submit_button(label="Delete Publisher")

    if submit_button:
        try:
            publisher_data = DeletePublisher(publisher_id=int(publisher_id))
            response = requests.delete(f"{base_url}/{publisher_id}")
            if response.status_code == 200:
                st.success("Publisher deleted successfully!")
            else:
                st.error(f"Failed to delete publisher: {response.json().get('detail', 'Unknown error')}")
        except ValidationError as e:
            st.error(f"Validation error: {e}")

def publishers_page():
    st.sidebar.title("Publisher Management")

    options = ["Create Publisher", "Search Publisher", "Update Publisher", "Delete Publisher"]
    choice = st.sidebar.selectbox("Select Operation", options)

    if choice == "Create Publisher":
        create_publisher()
    elif choice == "Search Publisher":
        search_publisher()
    elif choice == "Update Publisher":
        update_publisher()
    elif choice == "Delete Publisher":
        delete_publisher()
