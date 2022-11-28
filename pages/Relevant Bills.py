import streamlit as st
import sys
sys.path.insert(0, "..")

from bill import Bill
from Home import renderBills

limit = 20


if 'offset' not in st.session_state:
    st.session_state.offset = 0




st.title("Relevant Bills")

st.write("Using a daily updated database of thousands of posts from the popular subreddit r/Politics, Resolve can reccomend bills that are pertintent to current events.")

col1, col2 = st.columns(2)

with col1:
    def previous_page_click(*, limit):
        st.session_state.offset -= limit
        if st.session_state.offset < 0:
            st.session_state.offset = 0

    previous_page = st.button("Previous Page", on_click=previous_page_click, kwargs={"limit": limit}, key=3203498639046834)


with col2:
    def next_page_click(*, limit):
        st.session_state.offset += limit

    next_page = st.button("Next Page", on_click=next_page_click, kwargs={"limit": limit}, key=37509325902385928509)


print(st.session_state.offset)
bills = Bill.relevantBills(limit, st.session_state.offset)
renderBills(bills)
