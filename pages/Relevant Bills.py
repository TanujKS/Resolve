import streamlit as st
import sys
sys.path.insert(0, "..")

from bill import Bill
from Home import renderBills


st.title("Relevant Bills")

st.write("Using a daily updated database of thousands of posts from the popular subreddit r/Politics, Resolve can reccomend bills that are pertintent to current events.")

bills = Bill.relevantBills(20)
renderBills(bills)
