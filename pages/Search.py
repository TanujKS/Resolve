import sys
sys.path.insert(0, "..")
import streamlit as st
import requests
from bill import Bill
from utils import exceptions
from utils.render import renderBills

st.set_page_config(page_title="Resolve")




st.title("Search Resolve")

if 'new_session' not in st.session_state:
    st.session_state.new_session = True
    st.experimental_memo.clear()


with st.sidebar:
    st.write("Using machine learning to compare keywords to a database of Congressional bills, Resolve can help you find bills that are important to you.")


query = st.text_input("Search with keywords")




@st.experimental_memo(show_spinner=False, experimental_allow_widgets=True)
def getSearchBills(query, update_status): #for caching purposes
    return Bill.searchBills(query, update_status)


def main():
    if query:
        update_status = requests.get("https://us-central1-resolve-87f2f.cloudfunctions.net/updateStatus").json()
        bills = getSearchBills(query, update_status)
        renderBills(bills)


try:
    main()
except exceptions.BillException as error:
    st.error(error)
