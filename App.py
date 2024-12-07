import json
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Civitas Dashboard", layout="wide", page_icon="🏗")
st.title("🏗 Welcome to Civitas Construction Dashboard!")
st.markdown("### Your all-in-one tool for managing construction projects 🚀")
st.markdown("---")

# Initialize Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'projects' not in st.session_state:
    st.session_state.projects = []
if 'username' not in st.session_state:
    st.session_state.username = None

# Custom serializer for datetime objects
def custom_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

# Save projects to JSON
def save_projects():
    try:
        with open("projects.json", "w") as file:
            json.dump(st.session_state.projects, file, indent=4, default=custom_serializer)
    except Exception as e:
        st.error(f"Error saving projects: {e}")

# Load projects from JSON
def load_projects():
    try:
        with open("projects.json", "r") as file:
            st.session_state.projects = json.load(file)
    except FileNotFoundError:
        st.session_state.projects = []

# Login/Register System
def login_register():
    with st.sidebar:
        st.header("🔑 Login/Register")
        action_choice = st.radio("Choose an action", ["Login", "Register"])

        if action_choice == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if username == "admin" and password == "admin":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Admin"
                    st.session_state.username = username
                    st.success(f"Welcome back, Admin!")
                elif username == "user" and password == "user":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "User "
                    st.session_state.username = username
                    st.success(f"Welcome back, {username}!")
                else:
                    st.error("Invalid credentials. Try again.")
                    st.warning("Make sure you enter 'admin' as the username and password to test the login!")

        elif action_choice == "Register":
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            if st.button("Register"):
                if new_username and new_password and new_password == confirm_password:
                    st.success(f"Account created successfully for {new_username}!")
                else:
                    st.error("Passwords do not match or fields are empty.")

# Display Login/Register if not logged in
if not st.session_state.logged_in:
    login_register()
else:
    st.sidebar.header(f"👋 Welcome, {st.session_state.username}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    # Tabs for Dashboard
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📂 Project Overview", "📊 Progress Tracking", "💰 Financials",
                                                  "✅ Task Management", "📄 Documents", "💼 Interim Claims"])

    # Tab 1: Project Overview
    with tab1:
        st.header("📂 Project Overview")
        st.markdown("View and manage all your projects here.")
        project_action = st.radio("Choose an action", ["Register New Project", "View Existing Projects"])

        if project_action == "Register New Project":
            with st.form(key="project_form"):
                col1, col2 = st.columns(2)
                with col1:
                    project_name = st.text_input("Project Name")
                    project_id = st.text_input("Project ID")
                    client_name = st.text_input("Client Name")
                with col2:
                    start_date = st.date_input("Start Date")
                    end_date = st.date_input("End Date", min_value=start_date)
                    budget = st.number_input("Budget ($)", min_value=0, value=100000)

                submit = st.form_submit_button("Register Project")
                if submit:
                    try:
                        if not project_name or not project_id or not client_name:
                            raise ValueError("All fields are required!")
                        project = {
                            "name": project_name,
                            "id": project_id,
                            "client": client_name,
                            "start_date": start_date,
                            "end_date": end_date,
                            "budget": budget
                        }
                        st.session_state.projects.append(project)
                        save_projects()
                        st.success(f"Project '{project_name}' registered successfully!")
                    except ValueError as ve:
                        st.error(ve)

        elif project_action == "View Existing Projects":
            if st.session_state.projects:
                st.write(pd.DataFrame(st.session_state.projects))
            else:
                st.warning("No projects registered yet.")

    # Additional tabs can be implemented similarly
    # Tab 2: Progress Tracking
    with tab2:
        st.header("📊 Progress Tracking")
        st.markdown("Track the progress of your projects here.")
        # Implementation for progress tracking goes here

    # Tab 3: Financials
    with tab3:
        st.header("💰 Financials")
        st.markdown("Manage your project's financials.")
        # Implementation for financial management goes here

    # Tab 4: Task Management
    with tab4:
        st.header("✅ Task Management")
        st.markdown("Manage tasks related to your projects.")
        # Implementation for task management goes here

    # Tab 5: Documents
    with tab5:
        st.header("📄 Documents")
        st.markdown("Upload and manage project documents.")
        # Implementation for document management goes here

    # Tab 6: Interim Claims
    with tab6:
        st.header("💼 Interim Claims")
        st.markdown("Manage interim claims for your projects.")
        # Implementation for interim claims goes here

