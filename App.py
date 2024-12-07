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
def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'projects' not in st.session_state:
        st.session_state.projects = []
    if 'username' not in st.session_state:
        st.session_state.username = None

initialize_session_state()

# Custom serializer for datetime objects
def custom_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

# Save and Load Projects
def save_projects():
    try:
        with open("projects.json", "w") as file:
            json.dump(st.session_state.projects, file, indent=4, default=custom_serializer)
    except Exception as e:
        st.error(f"Error saving projects: {e}")

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
                    st.session_state.user_role = "User"
                    st.session_state.username = username
                    st.success(f"Welcome back, {username}!")
                else:
                    st.error("Invalid credentials. Try again.")

        elif action_choice == "Register":
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            if st.button("Register"):
                if new_username and new_password == confirm_password:
                    st.success(f"Account created successfully for {new_username}!")
                else:
                    st.error("Passwords do not match or fields are empty.")

# Main Dashboard
def dashboard():
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
                register_new_project()
            elif project_action == "View Existing Projects":
                view_existing_projects()

        # Tab 2: Progress Tracking
        with tab2:
            st.header("📊 Progress Tracking")
            st.write("Monitor project progress with interactive visuals.")
            if st.session_state.projects:
                track_project_progress()

        # Tab 3: Financials
        with tab3:
            st.header("💰 Financial Overview")
            st.write("Track budgets and spending dynamically.")
            if st.session_state.projects:
                track_project_financials()

        # Tab 4: Task Management
        with tab4:
            st.header("✅ Task Management")
            st.write("Assign tasks and track their progress.")
            if st.session_state.projects:
                manage_tasks()

        # Tab 5: Documents
        with tab5:
            st.header("📄 Document Management")
            st.write("Upload and manage project documents.")
            if st.session_state.projects:
                manage_documents()

        # Tab 6: Interim Claims
        with tab6:
            st.header("💼 Interim Claims")
            st.write("Manage interim claims and track payments.")
            if st.session_state.projects:
                manage_interim_claims()

# Register New Project
def register_new_project():
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
            if not project_name or not project_id or not client_name:
                st.error("All fields are required!")
            else:
                new_project = {
                    "name": project_name,
                    "id": project_id,
                    "client": client_name,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "budget": budget,
                    "progress": 0,
                    "tasks": [],
                    "documents": [],
                    "interim_claims": []
                }

                st.session_state.projects.append(new_project)
                save_projects()
                st.success(f"Project {project_name} registered successfully!")

# View Existing Projects
def view_existing_projects():
    load_projects()

    if st.session_state.projects:
        project_names = [proj["name"] for proj in st.session_state.projects]
        selected_project = st.selectbox("Select a Project to Track", project_names,
                                        key="existing_project_select")
        project_data = next(proj for proj in st.session_state.projects if proj["name"] == selected_project)
        st.write("**Project Details:**")
        st.json(project_data)

        # Option to delete project
        if st.button("Delete Project", key=f"delete_{selected_project}"):
            st.session_state.projects = [proj for proj in st.session_state.projects if
                                         proj["name"] != selected_project]
            save_projects()
            st.success(f"Project {selected_project} deleted successfully!")
    else:
        st.info("No projects available. Please register a new project.")

# Track Project Progress
def track_project_progress():
    project_names = [proj["name"] for proj in st.session_state.projects]
    selected_project = st.selectbox("Select a Project to Track", project_names, key="progress_tracking_select")
    project_data = next(proj for proj in st.session_state.projects if proj["name"] == selected_project)

    if "progress" not in project_data:
        project_data["progress"] = 0  # Initialize progress if not present

    progress = st.slider("Update Progress (%)", 0, 100, project_data["progress"],
                         key=f"progress_slider_{selected_project}")
    project_data["progress"] = progress
    save_projects()
    st.success(f"Updated progress for {project_data['name']} to {progress}%!")

    # Display progress using a gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=progress,
        title={"text": "Project Progress"},
        gauge={"axis": {"range": [0, 100]}}))
    st.plotly_chart(fig)

    # Display overall progress graph
    st.subheader("Project Progress - Milestone Overview")
    milestone_data = {
        'Milestone': ['Planning', 'Design', 'Construction', 'Completion'],
        'Progress': [20, 40, 60, progress]
    }
    progress_fig = px.bar(milestone_data, x='Milestone', y='Progress', title="Project Milestones")
    st.plotly_chart(progress_fig)

# Track Financials
def track_project_financials():
    project_names = [proj["name"] for proj in st.session_state.projects]
    selected_project = st.selectbox("Select a Project for Financials", project_names, key="financials_select")
    project_data = next(proj for proj in st.session_state.projects if proj["name"] == selected_project)

    spent = st.number_input("Spent Amount ($)", min_value=0, value=0, key=f"spent_input_{selected_project}")
    remaining = project_data["budget"] - spent
    st.write(f"Remaining Budget: ${remaining}")

    # Display financial breakdown
    financial_data = {
        "Spent": spent,
        "Remaining": remaining,
        "Total Budget": project_data["budget"]
    }

    fig = go.Figure(go.Pie(labels=list(financial_data.keys()), values=list(financial_data.values())))
    st.plotly_chart(fig)

# Task Management (Placeholder Function)
def manage_tasks():
    st.write("Here you can manage tasks for the selected project.")
    st.info("Task management functionality coming soon!")

# Document Management (Placeholder Function)
def manage_documents():
    st.write("Here you can manage documents for the selected project.")
    st.info("Document management functionality coming soon!")

# Interim Claims (Placeholder Function)
def manage_interim_claims():
    st.write("Here you can manage interim claims for the selected project.")
    st.info("Interim claims functionality coming soon!")

# Run the Dashboard
dashboard()
