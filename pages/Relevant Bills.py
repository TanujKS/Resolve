import sys
sys.path.insert(0, "..")
import streamlit as st
import time
from bill import Bill
from utils import exceptions
from utils.render import renderBills

limit = 20
st.set_page_config(page_title="Resolve")


if 'offset' not in st.session_state:
    st.session_state.offset = 0
    st.experimental_memo.clear()




st.title("Relevant Bills")


with st.sidebar:
    st.write("Using a daily updated database of thousands of posts from the popular subreddit r/Politics, Resolve can recommend bills that are pertinent to current events.")






col1, col2, col3 = st.columns(3)

with col1:
    def previous_page_click(*, limit):
        st.session_state.offset -= limit
        if st.session_state.offset < 0:
            st.session_state.offset = 0

    previous_page = st.button("Previous Page", on_click=previous_page_click, kwargs={"limit": limit}, key=time.time())


with col2:
    st.write(f"Page {int(st.session_state.offset/20 + 1)}")

with col3:
    def next_page_click(*, limit):
        st.session_state.offset += limit

    next_page = st.button("Next Page", on_click=next_page_click, kwargs={"limit": limit}, key=time.time())






@st.experimental_memo(show_spinner=False, experimental_allow_widgets=True)
def getRelevantBills(limit, offset):
    return Bill.relevantBills(limit, offset)


bills = getRelevantBills(limit, st.session_state.offset)
renderBills(bills)
