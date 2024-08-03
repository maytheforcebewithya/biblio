import streamlit as st
import requests
import re
import datetime
import pandas as pd
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError, ValidationInfo
import os

API_URL = os.getenv('API_URL', 'http://localhost:8000')

base_url = f"{API_URL}/patron"

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

def create_patron():
    st.title("Create Patron")

    with st.form(key="create_patron_form"):
        patron_id = st.text_input("Patron ID")
        patron_first_name = st.text_input("First Name")
        patron_last_name = st.text_input("Last Name")
        patron_email = st.text_input("Email")
        patron_phone = st.text_input("Phone")

        submit_button = st.form_submit_button(label="Create Patron")

    if submit_button:
        try:
            patron_data = CreatePatron(
                patron_id=patron_id.upper(),
                patron_first_name=patron_first_name.capitalize(),
                patron_last_name=patron_last_name.capitalize(),
                patron_email=patron_email,
                patron_phone=patron_phone
            )
            response = requests.post(f"{base_url}/", json=patron_data.dict())
            if response.status_code == 200:
                st.success("Patron created successfully!")
            else:
                st.error(f"Failed to create patron: {response.json().get('detail', 'Unknown error')}")
        except ValidationError as e:
            st.error(f"Validation error: {e}")

def search_patron():
    st.title("Search Patron")

    show_all = st.checkbox("Show All Patrons")
    if show_all:
        response = requests.get(f"{base_url}/all")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                df = pd.DataFrame(data)
                desired_order = ['id', 'first_name', 'last_name', 'email', 'phone', 'status', 'fine']
                st.dataframe(df, use_container_width=True, hide_index=True, column_order=desired_order)
            else:
                st.error("Data format is not a list.")
        else:
            st.error(f"Failed to fetch patrons: {response.json().get('detail', 'Unknown error')}")
    
    else:
        search_type = st.selectbox("Search by:", ["ID", "Name", "Fine"])

        if search_type == "ID":
            patron_id = st.text_input("Enter Patron ID")
            if st.button("Search"):
                response = requests.get(f"{base_url}/id/{patron_id}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict):
                        df = pd.DataFrame([data])
                        desired_order = ['id', 'first_name', 'last_name', 'email', 'phone', 'status', 'fine']
                        st.dataframe(df, use_container_width=True, key=None, column_order=desired_order, hide_index=True)
                    else:
                        st.error("Data format is not a dictionary.")
                else:
                    st.error(f"Failed to fetch patron: {response.json().get('detail', 'Unknown error')}")

        elif search_type == "Name":
            patron_name = st.text_input("Enter Patron Name")
            if st.button("Search"):
                response = requests.get(f"{base_url}/name/{patron_name}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                        desired_order = ['id', 'first_name', 'last_name', 'email', 'phone', 'status', 'fine']
                        st.dataframe(df, use_container_width=True, key=None, column_order=desired_order, hide_index=True)
                    else:
                        st.error("Data format is not a list.")
                else:
                    st.error(f"Failed to fetch patrons: {response.json().get('detail', 'Unknown error')}")

        elif search_type == "Fine":
            patron_fine = st.slider("Select Patron Fine", min_value=0, max_value=1000, step=1)
            if st.button("Search"):
                response = requests.get(f"{base_url}/fine/{patron_fine}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                        st.dataframe(df, use_container_width=True, key=None, column_order=desired_order, hide_index=True)
                    else:
                        st.error("Data format is not a list.")
                else:
                    st.error(f"Failed to fetch patrons: {response.json().get('detail', 'Unknown error')}")

def update_patron():
    st.title("Update Patron")

    with st.form(key="update_patron_form"):
        patron_id = st.text_input("Patron ID")
        patron_first_name = st.text_input("First Name", help="Leave blank if not changing")
        patron_last_name = st.text_input("Last Name", help="Leave blank if not changing")
        patron_email = st.text_input("Email", help="Leave blank if not changing")
        patron_phone = st.text_input("Phone", help="Leave blank if not changing")

        submit_button = st.form_submit_button(label="Update Patron")

    if submit_button:
        try:
            patron_data = UpdatePatron(
                patron_first_name=patron_first_name or None,
                patron_last_name=patron_last_name or None,
                patron_email=patron_email or None,
                patron_phone=patron_phone or None
            )
            response = requests.patch(f"{base_url}/{patron_id}", json=patron_data.dict(exclude_none=True))
            if response.status_code == 200:
                st.success("Patron updated successfully!")
            else:
                st.error(f"Failed to update patron: {response.json().get('detail', 'Unknown error')}")
        except ValidationError as e:
            st.error(f"Validation error: {e}")

def delete_patron():
    st.title("Delete Patron")

    with st.form(key="delete_patron_form"):
        patron_id = st.text_input("Patron ID")

        submit_button = st.form_submit_button(label="Delete Patron")

    if submit_button:
        try:
            patron_data = DeletePatron(patron_id=patron_id)
            response = requests.delete(f"{base_url}/{patron_id}")
            if response.status_code == 200:
                st.success("Patron deleted successfully!")
            else:
                st.error(f"Failed to delete patron: {response.json().get('detail', 'Unknown error')}")
                st.write(f"Status code: {response.status_code}")
                st.write(f"Response content: {response.content}")
        except ValidationError as e:
            st.error(f"Validation error: {e}")

def patrons_page():
    st.sidebar.title("Patron Management")

    options = ["Create Patron", "Search Patron", "Update Patron", "Delete Patron"]
    choice = st.sidebar.selectbox("Select Operation", options)

    if choice == "Create Patron":
        create_patron()
    elif choice == "Search Patron":
        search_patron()
    elif choice == "Update Patron":
        update_patron()
    elif choice == "Delete Patron":
        delete_patron()