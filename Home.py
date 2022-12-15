import streamlit as st
from bill import Bill
import json
from dotenv import load_dotenv
from utils import exceptions
from utils.render import renderBills
import traceback

load_dotenv()
st.set_page_config(page_title="Resolve")


if 'home_offset' not in st.session_state:
    st.session_state.home_offset = 0
    st.session_state.home_page = 1



st.title("Welcome to Resolve")


with st.sidebar:
    st.header("Our Mission")
    st.write("Too many citizens here in the United States are discouraged from participating in politics with all the political jargon and legal language. Resolve aims to solve that problem by using advanced Artificial Intelligence and Machine Learning to explain Congressional bills in language humans can understand.")

    st.header("Congressional Bills")
    st.subheader("What are Congressional bills?")
    st.write("Bills are a proposal put before a body of Congress. Bills are written by a Representative, then handed over a committee of experts on the topic. It is then voted on with a simple majority and passed to the other branch of Congress which then repeats the process. After passing both the House and the Senate it is put on the President's desk where they can either veto it or pass it as law. Bills are denoted by the House they originated in, such as HR for House Resolutions and S for Senate Resolutions.")
    st.write("Tip: Use the 'More Information' button when viewing a bill to see what stage it's currently in!")

    st.subheader("What are Joint Resolutions?")
    st.write("Joint resolutions are very similar to bills, but are generally used for specific matters or amendments to the Constitution, where they do not require the signature of the President if they have a 2/3s vote from both Houses. Joint Resolutions are denoted by the house they originated in followed by JRES (Joint RESolution)")

    st.subheader("What are Concurrent Resolutions?")
    st.write("Concurrent resolutions require approval from both Houses but do not require the Signature of the President as they do not have the effect of the law. They are mainly used to convey the sentiment, views, or beliefs of Congress as a whole. Concurrent resolutions are denoted by the house they originated in followed by CONRES (CONcurrent RESolution)")

    st.subheader("What are Simple Resolutions?")
    st.write("Simple resolutions is a proposal only pertaining to one branch of Congress. It does not require the approval of the other House or the President as it does not have the force of law. They are generally used to express the sentiment, views, or beliefs of a single House. Simple resolutions are denoted as the House they pertain too followed by RES (RESolution)")




bill_number = st.number_input("Search by Bill number",
    min_value=0,
    step=1
    )

st.write("Or Search By:")
col1, col2, col3, col4 = st.columns(4)

with col1:
    congress = st.selectbox(
        'Select a Congress session',
        (Bill.congresses)
        )

    type_of_legislation = st.selectbox(
    'Select a type of bill',
    (item for key, item in Bill.types_of_legislation.items())
    )


with col2:
    limit = st.number_input("Results per page", min_value = 1, max_value = 250, value = 20)
    sort_by = st.selectbox(
        'Sort By',
        list(Bill.types_of_sort.keys())
    )


with col3:
    def previous_page_click(*, limit):
        st.session_state.home_offset -= limit
        st.session_state.home_page -= 1
        if st.session_state.home_offset < 0:
            st.session_state.home_offset = 0
            st.session_state.home_page = 1

    def next_page_click(*, limit):
        st.session_state.home_offset += limit
        st.session_state.home_page += 1

    st.markdown("#")
    next_page = st.button("Next Page", on_click=next_page_click, kwargs={"limit": limit})
    st.markdown("#")
    previous_page = st.button("Previous Page", on_click=previous_page_click, kwargs={"limit": limit})


with col4:
    st.markdown("#")
    st.markdown("#")
    st.subheader(f"Page {st.session_state.home_page}")




@st.experimental_memo(show_spinner=False, experimental_allow_widgets=True)
def getRecentBills(congress, type, *, sort, offset, limit):
    return Bill.recentBills(congress, type, sort=sort, offset=offset, limit=limit)


@st.experimental_memo(show_spinner=False, experimental_allow_widgets=True)
def getBillsByNumber(number, *, limit, offset):
    bills = []

    max = offset + limit
    if (max > len(Bill.congresses)):
        max = len(Bill.congresses)

    for index in range(offset, max):
        c = Bill.congresses[0] - index

        bill = Bill(c, Bill.types_of_legislation_display[type_of_legislation], number=bill_number)
        try:
            bill.title = bill.getTitle()
        except:
            pass
        bills.append(bill)
    return bills


def main():
    if bill_number == 0:
        bills = getRecentBills(congress, Bill.types_of_legislation_display[type_of_legislation], sort=Bill.types_of_sort[sort_by], offset=st.session_state.home_offset, limit=limit)
        renderBills(bills)
    else:
        bills = getBillsByNumber(bill_number, limit=limit, offset=st.session_state.home_offset)
        renderBills(bills, raise_no_bill_error=False)



try:
    main()
except exceptions.BillException as error:
    st.error(error)
