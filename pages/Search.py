import streamlit as st
import sys
sys.path.insert(0, "..")

from bill import Bill
from Home import renderBills


st.title("Search Resolve")

st.write("Using a cosine similarity model to compare keywords to a constantly updating database of Congressional bills, Resolve can help you find bills that are important to you")

query = st.text_input("Search with keywords")

if query:
    bills = Bill.searchBills(query)
    renderBills(bills)
