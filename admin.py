# admin login/signup
# admin dashboard
#


import streamlit as st
from streamlit import session_state
import json
import os
import numpy as np
from dotenv import load_dotenv
from PIL import Image
from openai import OpenAI

import os

session_state = st.session_state
if "user_index" not in st.session_state:
    st.session_state["user_index"] = 0


def signup(json_file_path="admin.json"):
    st.title("Signup Page")
    with st.form("signup_form"):
        st.write("Fill in the details below to create an account:")
        name = st.text_input("Name:")
        email = st.text_input("Email:")
        age = st.number_input("Age:", min_value=0, max_value=120)
        sex = st.radio("Sex:", ("Male", "Female", "Other"))
        password = st.text_input("Password:", type="password")
        confirm_password = st.text_input("Confirm Password:", type="password")

        if st.form_submit_button("Signup"):
            if password == confirm_password:
                user = create_account(
                    name,
                    email,
                    age,
                    sex,
                    password,
                    json_file_path,
                )
                session_state["logged_in"] = True
                session_state["user_info"] = user
            else:
                st.error("Passwords do not match. Please try again.")


def check_login(username, password, json_file_path="admin.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)

        for user in data["admins"]:
            if user["email"] == username and user["password"] == password:
                session_state["logged_in"] = True
                session_state["user_info"] = user
                st.success("Login successful!")
                return user
        return None
    except Exception as e:
        st.error(f"Error checking login: {e}")
        return None


def initialize_database(json_file_path="admin.json"):
    try:
        if not os.path.exists(json_file_path):
            data = {"admins": []}
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file)
    except Exception as e:
        print(f"Error initializing database: {e}")


def create_account(
    name,
    email,
    age,
    sex,
    password,
    json_file_path="admin.json",
):
    try:
        # Check if the JSON file exists or is empty
        if not os.path.exists(json_file_path) or os.stat(json_file_path).st_size == 0:
            data = {"admins": []}
        else:
            with open(json_file_path, "r") as json_file:
                data = json.load(json_file)

        # Append new user data to the JSON structure
        user_info = {
            "name": name,
            "email": email,
            "age": age,
            "sex": sex,
            "password": password,
        }
        for user in data["admins"]:
            if user["email"] == email:
                st.warning("User already exists. Please login.")
                return None
        data["admins"].append(user_info)

        # Save the updated data to JSON
        with open(json_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        st.success("Account created successfully! You can now login.")
        return user_info
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating account: {e}")
        return None


def login(json_file_path="admin.json"):
    st.title("Login Page")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    login_button = st.button("Login")

    if login_button:
        user = check_login(username, password, json_file_path)
        if user is not None:
            session_state["logged_in"] = True
            session_state["user_info"] = user
        else:
            st.error("Invalid credentials. Please try again.")


def get_user_info(email, json_file_path="admin.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
            for user in data["admins"]:
                if user["email"] == email:
                    return user
        return None
    except Exception as e:
        st.error(f"Error getting user information: {e}")
        return None


def render_dashboard(user_info, json_file_path="admin.json"):
    try:
        # add profile picture
        st.title(f"Welcome to the Dashboard, {user_info['name']}!")

        st.subheader("Admin Information:")
        st.write(f"Name: {user_info['name']}")
        st.write(f"Sex: {user_info['sex']}")
        st.write(f"Age: {user_info['age']}")
    except Exception as e:
        st.error(f"Error rendering dashboard: {e}")


def main(json_file_path="admin.json"):
    st.sidebar.title("COGITO - Mental Health Assistant")
    page = st.sidebar.radio(
        "Go to",
        (
            "Signup/Login",
            "Dashboard",
            "View Patient Details",
        ),
        key="COGITO - Mental Health Assistant",
    )

    if page == "Signup/Login":
        st.title("Signup/Login Page")
        login_or_signup = st.radio(
            "Select an option", ("Login", "Signup"), key="login_signup"
        )
        if login_or_signup == "Login":
            login(json_file_path)
        else:
            signup(json_file_path)

    elif page == "Dashboard":
        if session_state.get("logged_in"):
            render_dashboard(session_state["user_info"])
        else:
            st.warning("Please login/signup to view the dashboard.")

    elif page == "View Patient Details":
        if session_state.get("logged_in"):
            user_info = session_state["user_info"]
            st.title("View Patient Details")
            st.write("Select a patient to view their details:")
            patient_details = {}
            with open("patients.json", "r") as json_file:
                data = json.load(json_file)
                for patient in data["patients"]:
                    patient_details["Name: " + patient["name"] + ", Email: " + patient["email"]] = patient
            patient_names = list(patient_details.keys())
            patient_names.insert(0, "Select a patient")
            selected_patient = st.selectbox("Select a patient", patient_names)
            if selected_patient != "Select a patient":
                st.write("Patient Details:")
                st.subheader(f"Name: {patient_details[selected_patient]['name']}")
                st.markdown(f"Email: {patient_details[selected_patient]['email']}")
                st.markdown(f"Age: {patient_details[selected_patient]['age']}")
                st.markdown(f"Sex: {patient_details[selected_patient]['sex']}")
                st.markdown(f"Password: {patient_details[selected_patient]['password']}")
                st.write('\n')
                st.subheader("Mental Health Assessment:")
                st.write(f"Report {patient_details[selected_patient]['report']}")
                st.write('\n')
                st.subheader("Questionnaire:")
                for questions in patient_details[selected_patient]['questions']:
                    st.markdown(f"Question: {questions['question']}")
                    st.markdown(f"Patient response: {questions['response']}")
                    st.write('\n')
        else:
            st.warning("Please login/signup to view patient details.")

if __name__ == "__main__":
    initialize_database()
    main()
