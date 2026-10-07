import streamlit as st

def binary_search(arr, target):
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_val = arr[mid]

        if mid_val == target:
            return mid
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1

arr = st.text_input("Enter sorted array elements separated by space: ", value="1 2 3 4 5 6 7 8 9 10")
arr = [int(x) for x in arr.split()]
target = st.number_input("Enter target element: ")

if st.button("Search"):
    result = binary_search(arr, target)
    if result != -1:
        st.write(f"Element {target} found at index: {result}")
    else:
        st.write(f"Element {target} not found in the array")