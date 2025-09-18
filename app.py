
# New sidebar order and routing

import streamlit as st
import config

st.set_page_config(page_title=config.APP_TITLE, page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.sidebar.image("https://img.icons8.com/color/96/000000/factory.png", width=80)
st.sidebar.markdown(f"<h2 style='color:#fff;'>{config.APP_TITLE}</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border-top:1px solid #e3eafc;'>", unsafe_allow_html=True)
page = st.sidebar.radio("Navigation", [
    "Home",
    "Dashboard",
    "Data Browser",
    "NL→SQL Querying",
    "Database",
    "Tools",
    "Test Cases"
])

if page == "Home":
    st.switch_page("pages/01_Home.py")
elif page == "Dashboard":
    st.switch_page("pages/02_Dashboard.py")
elif page == "Data Browser":
    st.switch_page("pages/04_Data_Browser.py")
elif page == "NL→SQL Querying":
    st.switch_page("pages/03_Analytics_QA.py")
elif page == "Database":
    st.switch_page("pages/06_Database.py")
elif page == "Tools":
    st.switch_page("pages/08_Tools.py")
elif page == "Test Cases":
    st.switch_page("pages/07_Test_Cases.py")
