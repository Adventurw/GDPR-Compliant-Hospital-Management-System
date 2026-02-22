import streamlit as st
import pandas as pd
from datetime import datetime
from database import DatabaseManager
from auth import Authentication
from encryption import DataProtection
from visualization import ActivityVisualization
from gdpr_compliance import GDPRCompliance



# Page configuration
st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide"
)

# Initialize classes
db = DatabaseManager()
auth = Authentication()
encryption = DataProtection()

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Initialize GDPR compliance
    gdpr = GDPRCompliance(db)

    # Show consent banner for all users
    gdpr.show_consent_banner()

    if not st.session_state.logged_in:
        auth.login_page()
        return
    
    user = st.session_state.user
    st.sidebar.title(f"Welcome, {user['username']}")
    st.sidebar.write(f"Role: {user['role']}")
    
    # Navigation based on role
    if user['role'] == 'admin':
        menu = ["Dashboard", "Patient Management", "Audit Logs", "GDPR Management","System Info"]
    elif user['role'] == 'doctor':
        menu = ["Dashboard", "View Patients"]
    else:  # receptionist
        menu = ["Dashboard", "Add Patient", "Edit Patient"]
    
    choice = st.sidebar.selectbox("Navigation", menu)
    
    # Display appropriate page based on selection
    if choice == "Dashboard":
        show_dashboard(user)
    elif choice == "Patient Management" and user['role'] == 'admin':
        patient_management(user)
    elif choice == "View Patients" and user['role'] in ['admin', 'doctor']:
        view_patients(user)
    elif choice == "Add Patient" and user['role'] in ['admin', 'receptionist']:
        add_patient(user)
    elif choice == "Edit Patient" and user['role'] in ['admin', 'receptionist']:
        edit_patient(user)
    elif choice == "Audit Logs" and user['role'] == 'admin':
        audit_logs(user)
    elif choice == "GDPR Management" and user['role'] == 'admin':
        gdpr_management(user, gdpr)    
    elif choice == "System Info":
        system_info(user)
    
    # Logout button
    if st.sidebar.button("Logout"):
        db.log_activity(user['user_id'], user['role'], "logout", "User logged out")
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

def show_dashboard(user):
    st.title("Hospital Management Dashboard")
    
    # System statistics
    conn = db.get_connection()
    
    # Get counts
    patient_count = pd.read_sql("SELECT COUNT(*) FROM patients", conn).iloc[0,0]
    user_count = pd.read_sql("SELECT COUNT(*) FROM users", conn).iloc[0,0]
    today_logs = pd.read_sql(
        "SELECT COUNT(*) FROM logs WHERE DATE(timestamp) = DATE('now')", 
        conn
    ).iloc[0,0]
    
    conn.close()
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Patients", patient_count)
    with col2:
        st.metric("System Users", user_count)
    with col3:
        st.metric("Today's Activities", today_logs)
    
    # Recent activities (last 5)
    if user['role'] == 'admin':
        st.subheader("Recent Activities")
        conn = db.get_connection()
        recent_logs = pd.read_sql(
            "SELECT * FROM logs ORDER BY timestamp DESC LIMIT 5", 
            conn
        )
        conn.close()
        st.dataframe(recent_logs)

     # REAL-TIME ACTIVITY GRAPHS (Admin only)
    if user['role'] == 'admin':
        st.subheader("Real-time Activity Analytics")
        
        viz = ActivityVisualization(db)
        
        col1, col2 = st.columns(2)
        
        with col1:
            viz.plot_daily_activity()
        
        with col2:
            viz.plot_role_activity()
        
        viz.plot_action_timeline()    

def patient_management(user):
    st.title("Patient Management")
    
    conn = db.get_connection()
    
    if st.button("Anonymize All Patient Data"):
        patients = pd.read_sql("SELECT * FROM patients", conn)
        for _, patient in patients.iterrows():
            anonymized_name = encryption.anonymize_name(patient['name'], patient['patient_id'])
            anonymized_contact = encryption.anonymize_contact(patient['contact'])
            
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE patients SET anonymized_name = ?, anonymized_contact = ? WHERE patient_id = ?",
                (anonymized_name, anonymized_contact, patient['patient_id'])
            )
        
        conn.commit()
        db.log_activity(user['user_id'], user['role'], "anonymization", "Anonymized all patient data")
        st.success("All patient data anonymized!")
    
    # Show patient data based on role
    if user['role'] == 'admin':
        patients = pd.read_sql("SELECT * FROM patients", conn)
        st.subheader("All Patient Data (Raw)")
        st.dataframe(patients)
    else:
        patients = pd.read_sql(
            "SELECT patient_id, anonymized_name, anonymized_contact, diagnosis, date_added FROM patients", 
            conn
        )
        st.subheader("Anonymized Patient Data")
        st.dataframe(patients)
    
    conn.close()

def view_patients(user):
    st.title("View Patients")
    
    conn = db.get_connection()
    
    # Doctors see only anonymized data
    patients = pd.read_sql(
        "SELECT patient_id, anonymized_name, anonymized_contact, diagnosis, date_added FROM patients", 
        conn
    )
    
    st.dataframe(patients)
    db.log_activity(user['user_id'], user['role'], "view", "Viewed patient list")
    
    conn.close()

def add_patient(user):
    st.title("Add New Patient")
    
    with st.form("add_patient_form"):
        name = st.text_input("Patient Name")
        contact = st.text_input("Contact Information")
        diagnosis = st.text_area("Diagnosis")
        
        submitted = st.form_submit_button("Add Patient")
        
        if submitted:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Add patient
            cursor.execute(
                "INSERT INTO patients (name, contact, diagnosis) VALUES (?, ?, ?)",
                (name, contact, diagnosis)
            )
            
            patient_id = cursor.lastrowid
            
            # Apply anonymization
            anonymized_name = encryption.anonymize_name(name, patient_id)
            anonymized_contact = encryption.anonymize_contact(contact)
            
            cursor.execute(
                "UPDATE patients SET anonymized_name = ?, anonymized_contact = ? WHERE patient_id = ?",
                (anonymized_name, anonymized_contact, patient_id)
            )
            
            conn.commit()
            conn.close()
            
            db.log_activity(user['user_id'], user['role'], "add_patient", f"Added patient: {name}")
            st.success("Patient added successfully!")

def edit_patient(user):
    st.title("Edit Patient")
    
    conn = db.get_connection()
    patients = pd.read_sql("SELECT patient_id, name, contact, diagnosis FROM patients", conn)
    conn.close()
    
    if not patients.empty:
        patient_options = [f"{row['patient_id']}: {row['name']}" for _, row in patients.iterrows()]
        selected_patient = st.selectbox("Select Patient to Edit", patient_options)
        
        if selected_patient:
            patient_id = int(selected_patient.split(":")[0])
            
            conn = db.get_connection()
            patient_data = pd.read_sql(
                f"SELECT * FROM patients WHERE patient_id = {patient_id}", 
                conn
            ).iloc[0]
            conn.close()
            
            with st.form("edit_patient_form"):
                diagnosis = st.text_area("Diagnosis", value=patient_data['diagnosis'])
                
                submitted = st.form_submit_button("Update Patient")
                
                if submitted:
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE patients SET diagnosis = ? WHERE patient_id = ?",
                        (diagnosis, patient_id)
                    )
                    conn.commit()
                    conn.close()
                    
                    db.log_activity(user['user_id'], user['role'], "edit_patient", f"Updated patient ID: {patient_id}")
                    st.success("Patient updated successfully!")

def audit_logs(user):
    st.title("Audit Logs")
    
    conn = db.get_connection()
    logs = pd.read_sql("SELECT * FROM logs ORDER BY timestamp DESC", conn)
    conn.close()
    
    st.dataframe(logs)
    
    # Export option
    if st.button("Export Logs to CSV"):
        csv = logs.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
def gdpr_management(user, gdpr):
    st.title("GDPR Compliance Management")
    gdpr.data_retention_management(user)
    
    # Add data export for right to access
    st.subheader("Data Subject Rights")
    
    if st.button("Export All User Data (Right to Access)"):
        conn = db.get_connection()
        all_data = pd.read_sql("SELECT * FROM logs", conn)
        conn.close()
        
        csv = all_data.to_csv(index=False)
        st.download_button(
            label="Download All Data as CSV",
            data=csv,
            file_name=f"gdpr_data_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )        

def system_info(user):
    st.title("System Information")
    
    st.subheader("CIA Triad Implementation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Confidentiality**")
        st.write("✓ Data anonymization")
        st.write("✓ Role-based access control")
        st.write("✓ Encryption for sensitive data")
    
    with col2:
        st.info("**Integrity**")
        st.write("✓ Comprehensive activity logging")
        st.write("✓ Data validation")
        st.write("✓ Audit trails")
    
    with col3:
        st.info("**Availability**")
        st.write("✓ Error handling")
        st.write("✓ Data backup/export")
        st.write("✓ System monitoring")
    
    st.subheader("GDPR Compliance Features")
    st.write("✓ Data minimization through anonymization")
    st.write("✓ Access controls and authentication")
    st.write("✓ Audit trails for accountability")
    st.write("✓ Data export capability")
    
    # System uptime (simplified)
    st.subheader("System Status")
    st.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.success("🟢 System Operational")

if __name__ == "__main__":
    main()