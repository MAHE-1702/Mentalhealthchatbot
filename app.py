import streamlit as st
import os

def main():
    st.title("COGITO - Mental Health Assistant")
    st.write("Welcome to COGITO, a mental health assistant that helps you track your mental health and provides you with resources to improve it.")
    page = st.radio(
        "Login or Signup as:",
        ("Admin", "Patient"),        key="login_signup",
    )
    if st.button("Login"):
        if page == "Admin":
            os.system('streamlit run admin.py')
        else:
            os.system('streamlit run patient.py')

if __name__ == "__main__":
    main()
