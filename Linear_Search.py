import streamlit as st

def linear_search(data, target):
    for i, item in enumerate(data):
        if item == target:
            return i
    return -1

data = [1, 3, 5, 7, 9]
target = st.number_input("Enter a number to search:")

result = linear_search(data, target)

if result != -1:
    st.write(f"{target} found at position {result} in the data list")
else:
    st.write(f"{target} not found in the data list")