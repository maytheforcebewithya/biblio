import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv('API_URL', 'http://localhost:8000')  # Fallback to localhost for local development

base_url = f"{API_URL}/bookcopy"

def get_bookcopy_count():
    st.title("Book Copy Count")
    response = requests.get(f"{base_url}/count")
    if response.status_code == 200:
        count = response.json()
        st.metric(label="Total Book Copies", value=count)
    else:
        st.error(f"Failed to fetch book copy count: {response.json().get('detail', 'Unknown error')}")

def show_overdue_bookcopies():
    st.title("Overdue Book Copies")
    response = requests.get(f"{base_url}/overdue")
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.error("Data format is not a list.")
    else:
        st.error(f"Failed to fetch overdue book copies: {response.json().get('detail', 'Unknown error')}")

def show_available_bookcopies():
    st.title("Available Book Copies")
    response = requests.get(f"{base_url}/available")
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            df = pd.DataFrame(data)
            columns_to_display = ['id', 'isbn', 'title', 'author', 'publisher']
            available_columns = [col for col in columns_to_display if col in df.columns]
            st.dataframe(df[available_columns], use_container_width=True, hide_index=True)
        else:
            st.error("Data format is not a list.")
    else:
        st.error(f"Failed to fetch available book copies: {response.json().get('detail', 'Unknown error')}")

def get_unreturned_count():
    st.title("Unreturned Book Copies Count")
    response = requests.get(f"{base_url}/unreturnedcount")
    if response.status_code == 200:
        count = response.json()
        st.metric(label="Unreturned Book Copies", value=count)
    else:
        st.error(f"Failed to fetch unreturned book copies count: {response.json().get('detail', 'Unknown error')}")

def bookcopies_page():
    st.sidebar.title("Book Copy Management")

    options = ["Book Copy Count", "Overdue Book Copies", "Available Book Copies", "Unreturned Book Copies Count"]
    choice = st.sidebar.selectbox("Select Operation", options)

    if choice == "Book Copy Count":
        get_bookcopy_count()
    elif choice == "Overdue Book Copies":
        show_overdue_bookcopies()
    elif choice == "Available Book Copies":
        show_available_bookcopies()
    elif choice == "Unreturned Book Copies Count":
        get_unreturned_count()

if __name__ == "__main__":
    bookcopies_page()