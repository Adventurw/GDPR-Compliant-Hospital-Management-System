import hashlib
import streamlit as st
from database import DatabaseManager

class Authentication:
    def __init__(self):
        self.db = DatabaseManager()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username, password):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Debug: Check what's actually in the database
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        db_user = cursor.fetchone()
        
        if db_user:
            st.write(f"Debug - Database record: {db_user}")
            st.write(f"Debug - Input password (hashed): {self.hash_password(password)}")
            st.write(f"Debug - Stored password: {db_user[2]}")
        
        hashed_password = self.hash_password(password)
        cursor.execute(
            "SELECT user_id, username, role FROM users WHERE username = ? AND password = ?",
            (username, hashed_password)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'role': user[2]
            }
        return None
    
    def login_page(self):
        st.title("Hospital Management System - Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                user = self.authenticate_user(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.logged_in = True
                    self.db.log_activity(user['user_id'], user['role'], "login", "User logged in")
                    st.success(f"Welcome {user['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")