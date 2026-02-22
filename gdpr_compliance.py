import streamlit as st
from datetime import datetime

class GDPRCompliance:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def show_consent_banner(self):
        """Display GDPR consent banner for new users"""
        if 'gdpr_consent' not in st.session_state:
            st.session_state.gdpr_consent = False
        
        if not st.session_state.gdpr_consent:
            with st.container():
                st.markdown("""
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b;">
                    <h3>🔒 GDPR Compliance Notice</h3>
                    <p>This system processes personal data in compliance with GDPR regulations.</p>
                    <p>By using this system, you acknowledge that:</p>
                    <ul>
                        <li>Personal data is processed lawfully and transparently</li>
                        <li>Data minimization principles are applied</li>
                        <li>Appropriate security measures are in place</li>
                        <li>Your activities are logged for security purposes</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("I Understand & Consent", type="primary"):
                        st.session_state.gdpr_consent = True
                        if 'user' in st.session_state:
                            self.db.log_activity(
                                st.session_state.user['user_id'],
                                st.session_state.user['role'],
                                "gdpr_consent",
                                "User accepted GDPR consent"
                            )
                        st.rerun()
                with col2:
                    if st.button("Learn More"):
                        st.info("Contact the Data Protection Officer for more information.")
    
    def data_retention_management(self, user):
        """Admin interface for data retention management"""
        if user['role'] == 'admin':
            st.subheader("GDPR Data Retention Management")
            
            col1, col2 = st.columns(2)
            
            with col1:
                retention_days = st.slider("Data Retention Period (days)", 
                                         min_value=7, max_value=365, value=30)
                
                if st.button("Apply Retention Policy"):
                    deleted_count = self.db.enforce_data_retention(retention_days)
                    st.success(f"Deleted {deleted_count} records older than {retention_days} days")
            
            with col2:
                st.info("""
                **GDPR Compliance Features:**
                - Right to be forgotten
                - Data minimization
                - Purpose limitation
                - Storage limitation
                - Integrity and confidentiality
                """)