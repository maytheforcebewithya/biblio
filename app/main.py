import streamlit as st
import requests
import pytz
from datetime import datetime
from streamlit_option_menu import option_menu
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.card import card
import os
from patrons import patrons_page
from authors import authors_page
from publishers import publishers_page
from books import books_page
from borrows import borrows_page
from bookcopies import bookcopies_page

st.set_page_config(
    page_title="biblio",
    page_icon="app/assets/biblio.png",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "About": "https://github.com/themohitnair/biblio"
    }
)

API_URL = os.getenv('API_URL', 'http://localhost:8000')

def get_metric(endpoint: str):
    try:
        response = requests.get(f"{API_URL}{endpoint}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(e)
        return None

def safe_get_metric(endpoint: str):
    value = get_metric(endpoint)
    return int(value) if value is not None else None

    

hide_streamlit_style = """<style>header[data-testid="stHeader"] {display: none;} ul[data-testid="main-menu"] {display: none;} div[data-testid="stStatusWidget"] {display: none;} div[data-testid="stToolbar"] {display: none;} #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}</style>"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def main_page():
    display_current_datetime()
    st.divider()
    st.markdown("<h1 style='text-align: center;'>Library Statistics</h1>", unsafe_allow_html=True)
    add_vertical_space(2)

    patron_count = safe_get_metric("/patron/count")
    patron_total_fine = safe_get_metric("/patron/finetotal")
    author_count = safe_get_metric("/author/count")
    book_count = safe_get_metric("/book/count")
    publisher_count = safe_get_metric("/publisher/count")
    transaction_count = safe_get_metric("/borrows/count")
    bookcopies_count = safe_get_metric("/bookcopy/count")
    unreturned_bookcopies_count = safe_get_metric("/bookcopy/unreturnedcount")
    available_copies = int(bookcopies_count) - int(unreturned_bookcopies_count) if bookcopies_count is not None and unreturned_bookcopies_count is not None else None

    col1, col2, col3, col4 = st.columns(4, gap="small", vertical_alignment="top")

    with col1:
        st.metric(label="Patrons", value=patron_count or "N/A")
        st.metric(label="Fines owed", value=f"₹ {patron_total_fine or 'N/A'}")

    with col2:
        st.metric(label="Books", value=book_count or "N/A")
        st.metric(label="Authors", value=author_count or "N/A")

    with col3:
        st.metric(label="Publishers", value=publisher_count or "N/A")
        st.metric(label="Transactions conducted", value=transaction_count or "N/A")
    
    with col4:
        st.metric(label="Copies Unreturned", value=unreturned_bookcopies_count or "N/A")
        st.metric(label="Copies Available", value=available_copies or "N/A")

    style_metric_cards(
        background_color="#000000",
        border_color="#4CAF50",
        border_radius_px=4,
        border_left_color="#4CAF50"
    )

def display_current_datetime():
    timezone = pytz.timezone("Asia/Kolkata")
    now = datetime.now(timezone)
    formatted_datetime = now.strftime("(%A) %B %d, %Y").strip()

    card(
    title="",
    text=formatted_datetime,
    styles={
        "card": {
            "width": "100%",
            "height": "100px", 
            "border-radius": "10px",
            "border": "2px solid #4CAF50",
            "padding": "0px",
            "margin": "0px",
        },
        "text": {
            "color": "#4CAF50",
            "font-size": "50px",
            "text-align": "center",
        }
    }
)

with st.sidebar:
    selected_page = option_menu(
        None,
        ["Home", "Patrons", "Authors", "Publishers", "Books", "Borrows", "Inventory"],
        icons=["house", "person", "pencil-square", "building", "book", "receipt-cutoff", "collection"],
        menu_icon=None,
        default_index=0,
        styles={
            "nav-link-selected": {"background-color": "#4CAF50", "color": "white"},
        }
    )

if selected_page == "Home":
    main_page()
elif selected_page == "Patrons":
    patrons_page()
elif selected_page == "Authors":
    authors_page()
elif selected_page == "Publishers":
    publishers_page()
elif selected_page == "Books":
    books_page()
elif selected_page == "Borrows":
    borrows_page()
elif selected_page == "Inventory":
    bookcopies_page()