import numpy
import streamlit as st

st.title("This is my first app")

value1 = st.slider(
     'Select a range of values for first argument',
     300.0, 500.0)

value2 = st.slider(
     'Select a range of values for second argument',
     180.0, 200.0)


addition = value1 + value2

st.write("The addition is",addition)
