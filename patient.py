import streamlit as st
from streamlit import session_state
import json
import os
import numpy as np
from dotenv import load_dotenv
from PIL import Image
from openai import OpenAI

load_dotenv()
import os
from openai import OpenAI

def mental_health_assistant(name, previous_question=None, previous_answer=None):
    try:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        if previous_question is None or previous_answer is None:
            prompt = f"""
            As a mental health adviser, your role is to offer a secure environment for individuals to freely express their thoughts and emotions. You acknowledge the difficulty in seeking assistance and reassure them of your unwavering support. With empathy and without judgment, you are committed to helping them face their mental health challenges. Your approach involves active listening, understanding, and providing thoughtful guidance. By asking pertinent questions, you aim to grasp each individual's unique mental health needs and offer the necessary support. Your goal is to ensure they feel validated, supported, and comprehended, and asking them questions to understand their mental health status as they navigate their journey towards well-being.
            """
        else:
            prompt = f"""
            {previous_question}
            Patient: {previous_answer}
            """
        messages = [{"role": "system", "content": prompt}]
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
            # model="gpt-3.5-turbo-0125",
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



def generate_medical_report(name, previous_questions=None, previous_responses=None):
    try:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        # Construct the prompt
        prompt = f"Patient: {name}\n\n"

        # If previous questions and responses are provided, append them to the prompt
        if previous_questions and previous_responses:
            for question, response in zip(previous_questions, previous_responses):
                prompt += f"Assistant: {question}\nPatient: {response}\n\n"

        else:
            prompt += "Assistant: Can you provide any relevant information about your condition?\nPatient:"

        # Add a request for medical report generation
        prompt += "\n\nGenerate a detailed medical report including any mental disorders and precautions needed."

        messages = [{"role": "system", "content": prompt}]

        # Request completion from OpenAI
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
            # model="gpt-3.5-turbo-0125",
        )

        # Extract report and precautions from response
        report = response.choices[0].message.content
        return report

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

session_state = st.session_state
if "user_index" not in st.session_state:
    st.session_state["user_index"] = 0


def signup(json_file_path="patients.json"):
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


def check_login(username, password, json_file_path="patients.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)

        for user in data["patients"]:
            if user["email"] == username and user["password"] == password:
                session_state["logged_in"] = True
                session_state["user_info"] = user
                st.success("Login successful!")
                return user
        return None
    except Exception as e:
        st.error(f"Error checking login: {e}")
        return None


def initialize_database(json_file_path="patients.json"):
    try:
        if not os.path.exists(json_file_path):
            data = {"patients": []}
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
    json_file_path="patients.json",
):
    try:
        # Check if the JSON file exists or is empty
        if not os.path.exists(json_file_path) or os.stat(json_file_path).st_size == 0:
            data = {"patients": []}
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
            "report": None,
            "questions": None,
        }
        for user in data["patients"]:
            if user["email"] == email:
                st.warning("User already exists. Please login.")
                return None
        data["patients"].append(user_info)

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


def login(json_file_path="patients.json"):
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


def get_user_info(email, json_file_path="patients.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
            for user in data["patients"]:
                if user["email"] == email:
                    return user
        return None
    except Exception as e:
        st.error(f"Error getting user information: {e}")
        return None

def render_dashboard(user_info, json_file_path="patients.json"):
    try:
        # add profile picture
        st.title(f"Welcome to the Dashboard, {user_info['name']}!")
        st.subheader("User Information:")
        st.write(f"Name: {user_info['name']}")
        st.write(f"Sex: {user_info['sex']}")
        st.write(f"Age: {user_info['age']}")
        
        # Check if medical report exists
        if user_info["report"] is not None:
            st.markdown("## Medical Report:")
            st.write(f"Report: {user_info['report']}")
        else:
            st.warning("You do not have a medical report yet.")
    except Exception as e:
        st.error(f"Error rendering dashboard: {e}")


def main(json_file_path="patients.json"):
    st.sidebar.title("COGITO - Mental Health Assistant")
    page = st.sidebar.radio(
        "Go to",
        (
            "Signup/Login",
            "Dashboard",
            "Take a mental health test",
            "Breathe-in, Breathe-out (Meditation)",
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
            
            
    elif page == "Take a mental health test":
        if session_state.get("logged_in"):
            user_info = session_state["user_info"]
            st.title("Take a mental health test")
            st.write("Answer the following questions to get a medical report.")
            with open(json_file_path, "r") as json_file:
                data = json.load(json_file)
                user_index = next(
                    (
                        i
                        for i, user in enumerate(data["patients"])
                        if user["email"] == session_state["user_info"]["email"]
                    ),
                    None,
                )
                if user_index is not None:
                    user_info = data["patients"][user_index]

            if user_info["questions"] is None:
                previous_response = None
                previous_question = None
            else:
                previous_response = user_info["questions"][-1]["response"]
                previous_question = user_info["questions"][-1]["question"]
            
            with st.form("mental_health_test_form"):
                question = mental_health_assistant(
                    user_info["name"],
                    previous_question,
                    previous_response,
                )
                st.markdown(question)
                response = st.text_input("Your response:")
                if st.form_submit_button("Next Question"):
                    if response is not None and len(response) > 0:
                        with open(json_file_path, "r+") as json_file:
                            data = json.load(json_file)
                            user_index = next(
                                (
                                    i
                                    for i, user in enumerate(data["patients"])
                                    if user["email"]
                                    == session_state["user_info"]["email"]
                                ),
                                None,
                            )
                            if user_index is not None:
                                user_info = data["patients"][user_index]
                                if user_info["questions"] is None:
                                    user_info["questions"] = []
                                user_info["questions"].append(
                                    {"question": question, "response": response}
                                )
                                session_state["user_info"] = user_info
                                json_file.seek(0)
                                json.dump(data, json_file, indent=4)
                                json_file.truncate()
                            else:
                                st.error("User not found.")
                        response = None
                    st.rerun()
                if st.form_submit_button("Complete the test and generate report"):
                    report = generate_medical_report(
                        user_info["name"],
                        [q["question"] for q in user_info["questions"]],
                        [q["response"] for q in user_info["questions"]
                    ])
                    st.write(report)
                    with open(json_file_path, "r+") as json_file:
                        data = json.load(json_file)
                        user_index = next(
                            (
                                i
                                for i, user in enumerate(data["patients"])
                                if user["email"] == session_state["user_info"]["email"]
                            ),
                            None,
                        )
                        if user_index is not None:
                            user_info = data["patients"][user_index]
                            user_info["report"] = report
                            session_state["user_info"] = user_info
                            json_file.seek(0)
                            json.dump(data, json_file, indent=4)
                            json_file.truncate()
                        else:
                            st.error("User not found.")
                    st.success("Report generated successfully!")
                    return

            # question = mental_health_assistant(
            #     user_info["name"],
            #     previous_question,
            #     previous_response,
            # )
            # st.markdown(question)
            # response = st.text_input("Your response:")
            # if st.button("Next Question"):
            #     if response is not None and len(response) > 0:
            #         with open(json_file_path, "r+") as json_file:
            #             data = json.load(json_file)
            #             user_index = next(
            #                 (
            #                     i
            #                     for i, user in enumerate(data["patients"])
            #                     if user["email"]
            #                     == session_state["user_info"]["email"]
            #                 ),
            #                 None,
            #             )
            #             if user_index is not None:
            #                 user_info = data["patients"][user_index]
            #                 if user_info["questions"] is None:
            #                     user_info["questions"] = []
            #                 user_info["questions"].append(
            #                     {"question": question, "response": response}
            #                 )
            #                 session_state["user_info"] = user_info
            #                 json_file.seek(0)
            #                 json.dump(data, json_file, indent=4)
            #                 json_file.truncate()
            #             else:
            #                 st.error("User not found.")
            #         response = None
            # if st.button("Complete the test and generate report"):
            #     report = generate_medical_report(
            #         user_info["name"],
            #         [q["question"] for q in user_info["questions"]],
            #         [q["response"] for q in user_info["questions"]]
            #     )
            #     with open(json_file_path, "r+") as json_file:
            #         data = json.load(json_file)
            #         user_index = next(
            #             (
            #                 i
            #                 for i, user in enumerate(data["patients"])
            #                 if user["email"] == session_state["user_info"]["email"]
            #             ),
            #             None,
            #         )
            #         if user_index is not None:
            #             user_info = data["patients"][user_index]
            #             user_info["report"] = report
            #             session_state["user_info"] = user_info
            #             json_file.seek(0)
            #             json.dump(data, json_file, indent=4)
            #             json_file.truncate()
            #         else:
            #             st.error("User not found.")
            #     st.success("Report generated successfully!")
            #     return
        else:
            st.warning("Please login/signup to chat.")
    # elif page == "Take a mental health test":
    #     if session_state.get("logged_in"):
    #         user_info = session_state["user_info"]
    #         st.title("Take a mental health test")
    #         st.write("Answer the following questions to get a medical report.")
    #         with open(json_file_path, "r") as json_file:
    #             data = json.load(json_file)
    #             user_index = next(
    #                 (
    #                     i
    #                     for i, user in enumerate(data["patients"])
    #                     if user["email"] == session_state["user_info"]["email"]
    #                 ),
    #                 None,
    #             )
    #             if user_index is not None:
    #                 user_info = data["patients"][user_index]

    #         if user_info["questions"] is None:
    #             previous_response = None
    #             previous_question = None
    #         else:
    #             previous_response = user_info["questions"][-1]["response"]
    #             previous_question = user_info["questions"][-1]["question"]

    #         question = mental_health_assistant(
    #             user_info["name"],
    #             previous_question,
    #             previous_response,
    #         )
    #         st.markdown(question)
    #         response = st.text_input("Your response:")
    #         if st.button("Next Question"):
    #             if response is not None and len(response) > 0:
    #                 with open(json_file_path, "r+") as json_file:
    #                     data = json.load(json_file)
    #                     user_index = next(
    #                         (
    #                             i
    #                             for i, user in enumerate(data["patients"])
    #                             if user["email"]
    #                             == session_state["user_info"]["email"]
    #                         ),
    #                         None,
    #                     )
    #                     if user_index is not None:
    #                         user_info = data["patients"][user_index]
    #                         if user_info["questions"] is None:
    #                             user_info["questions"] = []
    #                         user_info["questions"].append(
    #                             {"question": question, "response": response}
    #                         )
    #                         session_state["user_info"] = user_info
    #                         json_file.seek(0)
    #                         json.dump(data, json_file, indent=4)
    #                         json_file.truncate()
    #                     else:
    #                         st.error("User not found.")
    #                 response = None
    #         if st.button("Complete the test and generate report"):
    #             report = generate_medical_report(
    #                 user_info["name"],
    #                 [q["question"] for q in user_info["questions"]],
    #                 [q["response"] for q in user_info["questions"]]
    #             )
    #             with open(json_file_path, "r+") as json_file:
    #                 data = json.load(json_file)
    #                 user_index = next(
    #                     (
    #                         i
    #                         for i, user in enumerate(data["patients"])
    #                         if user["email"] == session_state["user_info"]["email"]
    #                     ),
    #                     None,
    #                 )
    #                 if user_index is not None:
    #                     user_info = data["patients"][user_index]
    #                     user_info["report"] = report
    #                     session_state["user_info"] = user_info
    #                     json_file.seek(0)
    #                     json.dump(data, json_file, indent=4)
    #                     json_file.truncate()
    #                 else:
    #                     st.error("User not found.")
    #             st.success("Report generated successfully!")
    #             return
    #     else:
    #         st.warning("Please login/signup to chat.")
            
            
    elif page == "Breathe-in, Breathe-out (Meditation)":
        if session_state.get("logged_in"):
            st.title("Breathe-in, Breathe-out (Meditation)")
            st.write("Meditate to calm your mind")
            st.video("https://youtu.be/8vkYJf8DOsc?si=G2skZLg0dsrZBkxa")
        else:
            st.warning("Please login/signup to meditate.")
    else:
        st.error("Invalid page selection.")
        
if __name__ == "__main__":
    initialize_database()
    main()
