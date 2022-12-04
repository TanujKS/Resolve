import sys
sys.path.insert(0, "..")
import streamlit as st
import time
import traceback
from bill import Bill
from utils import exceptions
from utils.render import renderBills

limit = 20
st.set_page_config(page_title="Resolve")


if 'relevant_offset' not in st.session_state:
    st.session_state.relevant_offset = 0
    st.session_state.relevant_page = 1
    st.experimental_memo.clear()




st.title("Relevant Bills")


with st.sidebar:
    st.write("Using a daily updated database of thousands of posts from the popular subreddit r/Politics, Resolve can recommend bills that are pertinent to current events.")




col1, col2, col3 = st.columns(3)

with col1:
    def previous_page_click(*, limit):
        st.session_state.relevant_offset -= limit
        st.session_state.relevant_page -= 1
        if st.session_state.relevant_offset < 0:
            st.session_state.relevant_offset = 0
            st.session_state.relevant_page = 1

    previous_page = st.button("Previous Page", on_click=previous_page_click, kwargs={"limit": limit}, key=time.time())


with col2:
    st.write(f"Page {st.session_state.relevant_page}")


with col3:
    def next_page_click(*, limit):
        st.session_state.relevant_offset += limit
        st.session_state.relevant_page += 1

    next_page = st.button("Next Page", on_click=next_page_click, kwargs={"limit": limit}, key=time.time())




@st.experimental_memo(show_spinner=False, experimental_allow_widgets=True)
def getRelevantBills(limit, offset):
    return Bill.relevantBills(limit, offset)


def main():
    bills = getRelevantBills(limit, st.session_state.relevant_offset)
    renderBills(bills)


main()
