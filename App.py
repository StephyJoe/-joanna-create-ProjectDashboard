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
                    st.session_state.user_role = "User"
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
                if new_username and new_password == confirm_password:
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

    # Tab 1: Project Overview with enhanced features
with tab1:
    st.header("📂 Project Overview")
    st.markdown("### View and manage all your projects here.")
    
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

    elif project_action == "View Existing Projects":
        load_projects()

        if st.session_state.projects:
            project_names = [proj["name"] for proj in st.session_state.projects]
            selected_project = st.selectbox("Select a Project to Track", project_names, key="existing_project_select")
            project_data = next(proj for proj in st.session_state.projects if proj["name"] == selected_project)

            # Display project details in a more visual format
            st.markdown("### Project Details")
            
            # Card Layout for project details
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Project Name:** {project_data['name']}")
                st.markdown(f"**Client:** {project_data['client']}")
                st.markdown(f"**Project ID:** {project_data['id']}")
            with col2:
                st.markdown(f"**Start Date:** {project_data['start_date']}")
                st.markdown(f"**End Date:** {project_data['end_date']}")
                st.markdown(f"**Budget:** ${project_data['budget']}")

            # Project Progress Bar
            st.markdown("### Project Progress")
            progress = project_data.get('progress', 0)
            progress_bar = st.progress(progress)
            st.markdown(f"Progress: {progress}%")

            # Visualize project status with a simple icon or color
            if progress == 100:
                st.markdown("<h4 style='color: green;'>✔️ Project Completed</h4>", unsafe_allow_html=True)
            elif progress >= 50:
                st.markdown("<h4 style='color: orange;'>⚡ Project in Progress</h4>", unsafe_allow_html=True)
            else:
                st.markdown("<h4 style='color: red;'>⏳ Project Not Started</h4>", unsafe_allow_html=True)

            # Collapsible Section for Financial Overview
            with st.expander("🔍 Financial Overview"):
                st.markdown(f"**Total Budget:** ${project_data['budget']}")
                st.markdown(f"**Amount Spent:** ${sum(task['cost'] for task in project_data['tasks'])}")
                
                # Pie chart for budget breakdown
                task_costs = [task["cost"] for task in project_data["tasks"]]
                task_labels = [task["name"] for task in project_data["tasks"]]
                fig, ax = plt.subplots()
                ax.pie(task_costs, labels=task_labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                st.pyplot(fig)

            # Collapsible Section for Task Management
            with st.expander("🗂️ Task Management"):
                if project_data["tasks"]:
                    task_names = [task["name"] for task in project_data["tasks"]]
                    for task in project_data["tasks"]:
                        st.progress(task["progress"])
                        st.markdown(f"**{task['name']}** - {task['progress']}% Complete")
                else:
                    st.info("No tasks added yet.")

            # Delete Project Button (Styled)
            st.markdown("<hr>", unsafe_allow_html=True)
            delete_button = st.button(f"❌ Delete Project: {selected_project}", key=f"delete_{selected_project}", help="This will permanently delete the project.")
            if delete_button:
                st.session_state.projects = [proj for proj in st.session_state.projects if proj["name"] != selected_project]
                save_projects()
                st.success(f"Project {selected_project} deleted successfully!")
        else:
            st.info("No projects available. Please register a new project.")

    # Tab 2: Progress Tracking
    with tab2:
        st.header("📊 Progress Tracking")
        st.write("Monitor project progress with interactive visuals.")
        if st.session_state.projects:
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

    # Tab 3: Financials
    with tab3:
        st.header("💰 Financial Overview")
        st.write("Track budgets and spending dynamically.")
        if st.session_state.projects:
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
            financial_fig = px.pie(names=list(financial_data.keys()), values=list(financial_data.values()),
                                   title="Budget Breakdown")
            st.plotly_chart(financial_fig)

    # Tab 4: Task Management
    with tab4:
        st.header("✅ Task Management")
        st.write("Assign tasks and track their progress.")
        if st.session_state.projects:
            project_names = [proj["name"] for proj in st.session_state.projects]
            selected_project = st.selectbox("Select a Project for Task Management", project_names,
                                            key="task_management_select")
            project_data = next(proj for proj in st.session_state.projects if proj["name"] == selected_project)

            task_action = st.radio("What would you like to do?", ["View Tasks", "Add New Task"])

            if task_action == "Add New Task":
                task_name = st.text_input("Task Name")
                task_due = st.date_input("Due Date")
                task_progress = st.slider("Task Progress (%)", 0, 100)
                if st.button("Add Task"):
                    project_data["tasks"].append({
                        "name": task_name,
                        "due": task_due.isoformat(),
                        "progress": task_progress
                    })
                    save_projects()
                    st.success(f"Task {task_name} added successfully!")

            elif task_action == "View Tasks":
                st.write(project_data["tasks"])

    # Tab 5: Documents
    with tab5:
        st.header("📄 Document Management")
        st.write("Upload and manage project documents.")
        if st.session_state.projects:
            project_names = [proj["name"] for proj in st.session_state.projects]
            selected_project = st.selectbox("Select a Project for Documents", project_names,
                                            key="document_management_select")
            project_data = next(proj for proj in st.session_state.projects if proj["name"] == selected_project)

            document = st.file_uploader("Upload Document", type=["pdf", "docx", "png", "jpg", "jpeg"])
            if document:
                project_data["documents"].append(document)
                save_projects()
                st.success(f"Document uploaded successfully!")

    # Tab 6: Interim Claims
    with tab6:
        st.header("💼 Interim Claims")
        st.write("Manage interim claims and track payments.")

        if st.session_state.projects:
            project_names = [proj["name"] for proj in st.session_state.projects]
            selected_project = st.selectbox("Select a Project for Interim Claims", project_names,
                                            key="interim_claims_select")
            project_data = next(proj for proj in st.session_state.projects if proj["name"] == selected_project)

            # Ensure interim_claims is initialized
            if "interim_claims" not in project_data:
                project_data["interim_claims"] = []

            interim_claim_action = st.radio("Interim Claims Action",
                                            ["View Claims", "Add New Claim", "Update Claim Status"])

            if interim_claim_action == "Add New Claim":
                # Add New Claim Form
                claim_amount = st.number_input("Claim Amount ($)", min_value=0)
                claim_status = st.selectbox("Claim Status", ["Pending", "Approved", "Rejected"])
                payment_schedule = st.date_input("Payment Schedule")
                notes = st.text_area("Claim Notes", placeholder="Add any notes or comments")

                if st.button("Add Claim"):
                    project_data["interim_claims"].append({
                        "amount": claim_amount,
                        "status": claim_status,
                        "payment_schedule": payment_schedule.isoformat(),
                        "notes": notes
                    })
                    save_projects()
                    st.success(f"Claim of ${claim_amount} added successfully!")

            elif interim_claim_action == "View Claims":
                # View Claims in Table Form with Search and Filter
                if project_data["interim_claims"]:
                    # Convert claims data to DataFrame
                    claims_df = pd.DataFrame(project_data["interim_claims"])
                    claims_df.index += 1  # Start indexing from 1
                    claims_df = claims_df.rename(columns={
                        "amount": "Claim Amount ($)",
                        "status": "Claim Status",
                        "payment_schedule": "Payment Schedule",
                        "notes": "Claim Notes"
                    })

                    # Filter by status, amount, or date
                    filter_status = st.selectbox("Filter by Claim Status", ["All", "Pending", "Approved", "Rejected"],
                                                 index=0)
                    if filter_status != "All":
                        claims_df = claims_df[claims_df["Claim Status"] == filter_status]

                    # Search bar for amount or notes
                    search_term = st.text_input("Search Claims", "")
                    if search_term:
                        claims_df = claims_df[
                            claims_df.apply(lambda row: row.astype(str).str.contains(search_term).any(), axis=1)]

                    # Sorting options
                    sort_by = st.selectbox("Sort Claims By", ["Claim Amount ($)", "Payment Schedule", "Claim Status"],
                                           index=0)
                    claims_df = claims_df.sort_values(by=sort_by, ascending=True)

                    # Display the claims table
                    st.dataframe(claims_df)

                    # Export Claims to CSV
                    if st.button("Export Claims to CSV"):
                        csv = claims_df.to_csv(index=False)
                        st.download_button("Download CSV", csv, "claims_data.csv", "text/csv")

                else:
                    st.info("No interim claims found for this project.")

            elif interim_claim_action == "Update Claim Status":
                # Update Existing Claim Status
                if project_data["interim_claims"]:
                    claim_options = [f"Claim #{idx + 1}" for idx in range(len(project_data["interim_claims"]))]
                    selected_claim = st.selectbox("Select a Claim to Update", claim_options)

                    # Get the selected claim's index
                    claim_idx = claim_options.index(selected_claim)
                    selected_claim_data = project_data["interim_claims"][claim_idx]

                    # Allow user to update the status of the selected claim
                    new_status = st.selectbox("Update Claim Status", ["Pending", "Approved", "Rejected"],
                                              index=["Pending", "Approved", "Rejected"].index(
                                                  selected_claim_data["status"]))

                    if st.button(f"Update Status for {selected_claim}"):
                        # Update the claim's status
                        project_data["interim_claims"][claim_idx]["status"] = new_status
                        save_projects()
                        st.success(f"The status for {selected_claim} has been updated to {new_status}.")
                else:
                    st.info("No interim claims found for this project.")

            # Claim History or Audit Trail
            if project_data["interim_claims"]:
                st.subheader("Claim History / Audit Trail")
                # Updated for handling missing 'notes'
                audit_data = []
                for claim in project_data["interim_claims"]:
                    audit_data.append({
                        "Claim Amount": claim["amount"],
                        "Status": claim["status"],
                        "Payment Schedule": claim["payment_schedule"],
                        "Notes": claim.get("notes", "No notes provided")
                        # Using get to avoid errors if 'notes' is missing
                    })

                if audit_data:
                    audit_df = pd.DataFrame(audit_data)
                    st.write(audit_df)
