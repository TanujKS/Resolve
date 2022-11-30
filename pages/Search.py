import streamlit as st
import sys
sys.path.insert(0, "..")
import requests
from bill import Bill
from Home import renderBills


st.title("Search Resolve")

if 'new_session' not in st.session_state:
    st.session_state.new_session = True
    st.experimental_memo.clear()


with st.sidebar:
    st.write("Using a cosine similarity model to compare keywords to a constantly updating database of Congressional bills, Resolve can help you find bills that are important to you")




query = st.text_input("Search with keywords")





@st.experimental_memo(show_spinner=False)
def getSearchBills(query, update_status): #for caching purposes
    return Bill.searchBills(query, update_status)


if query:
    update_status = requests.get("https://us-central1-resolve-87f2f.cloudfunctions.net/updateStatus").json()
    bills = getSearchBills(query, update_status)
    renderBills(bills)
