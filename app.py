import streamlit as st

activities = ["About", "PDF1", "PDF2", "PDF3"]
choice = st.sidebar.selectbox("Select Site", activities)


if choice == 'PDF1':
    st.title("1")

elif choice == "PDF2":
    st.title("2")

elif choice == "PDF3":
    st.title("3")
