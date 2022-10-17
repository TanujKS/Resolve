import streamlit as st
import pandas as pd
import numpy as np

st.title("Welcome to Billify")

option = st.selectbox(
    'Select a Congress',
    (117, 116, 115))

with st.expander("House Bills"):
    st.button("HR 1")
    st.button("HR 2")

with st.sidebar:
    st.header("Our Mission")
    st.write("With democracy being questioned everyday more and more here in the United States, it is essential that as many are involved with politics as possible.")

    st.header("Bills")
    st.write("What are bills?")

    st.header("Resolutions")
    st.write("What are resolutions?")
