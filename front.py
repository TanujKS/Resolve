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
    st.write("Our Mission")
