import streamlit as st
import requests
import pandas as pd
from pydantic import BaseModel, Field, ValidationError
from datetime import date
import json
import os

API_URL = os.getenv('API_URL', 'http://localhost:8000')

base_url = f"{API_URL}/borrows"

class AddBorrow(BaseModel):
    patron_id: str = Field(min_length=10, max_length=10)
    copy_id: int
    borrow_date: date

class ReturnBorrow(BaseModel):
    return_date: date

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

def create_borrow():
    st.title("Create Borrow")

    with st.form(key="create_borrow_form"):
        patron_id = st.text_input("Patron ID")
        copy_id = st.number_input("Copy ID", min_value=1, step=1)
        borrow_date = st.date_input("Borrow Date")

        submit_button = st.form_submit_button(label="Create Borrow")

    if submit_button:
        try:
            borrow_data = AddBorrow(
                patron_id=patron_id,
                copy_id=copy_id,
                borrow_date=borrow_date
            )
            
            json_data = json.dumps(borrow_data.dict(), cls=DateEncoder)
            
            response = requests.post(f"{base_url}/", data=json_data, headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                st.success("Borrow created successfully!")
            else:
                st.error(f"Failed to create borrow: {response.json().get('detail', 'Unknown error')}")
        except ValidationError as e:
            st.error(f"Validation error: {e}")

def show_borrows():
    st.title("Show Borrows")

    response = requests.get(f"{base_url}/all")
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.error("Data format is not a list.")
    else:
        st.error(f"Failed to fetch borrows: {response.json().get('detail', 'Unknown error')}")

def return_borrow():
    st.title("Return Borrow")

    with st.form(key="return_borrow_form"):
        transaction_id = st.number_input("Transaction ID", min_value=1, step=1)
        return_date = st.date_input("Return Date")

        submit_button = st.form_submit_button(label="Return Borrow")

    if submit_button:
        try:
            return_data = ReturnBorrow(return_date=return_date)
            response = requests.put(f"{base_url}/return/{transaction_id}", json=return_data.dict())
            if response.status_code == 200:
                st.success("Borrow returned successfully!")
            else:
                st.error(f"Failed to return borrow: {response.json().get('detail', 'Unknown error')}")
        except ValidationError as e:
            st.error(f"Validation error: {e}")

def get_borrows_by_patron():
    st.title("Get Borrows by Patron")

    patron_id = st.text_input("Patron ID")
    if st.button("Search"):
        response = requests.get(f"{base_url}/patron/{patron_id}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.error("Data format is not a list.")
        else:
            st.error(f"Failed to fetch borrows: {response.json().get('detail', 'Unknown error')}")

def get_borrows_by_isbn():
    st.title("Get Borrows by ISBN")

    isbn = st.text_input("ISBN")
    if st.button("Search"):
        response = requests.get(f"{base_url}/isbn/{isbn}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.error("Data format is not a list.")
        else:
            st.error(f"Failed to fetch borrows: {response.json().get('detail', 'Unknown error')}")

def borrows_page():
    st.sidebar.title("Borrow Management")

    options = ["Create Borrow", "Show Borrows", "Return Borrow", "Get Borrows by Patron", "Get Borrows by ISBN"]
    choice = st.sidebar.selectbox("Select Operation", options)

    if choice == "Create Borrow":
        create_borrow()
    elif choice == "Show Borrows":
        show_borrows()
    elif choice == "Return Borrow":
        return_borrow()
    elif choice == "Get Borrows by Patron":
        get_borrows_by_patron()
    elif choice == "Get Borrows by ISBN":
        get_borrows_by_isbn()