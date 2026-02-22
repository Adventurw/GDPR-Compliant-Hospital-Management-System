import hashlib
from cryptography.fernet import Fernet
import streamlit as st

class DataProtection:
    def __init__(self):
        # In production, store this key securely
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)
        try:
            with open('encryption_key.key', 'rb') as key_file:
                self.key = key_file.read()
        except FileNotFoundError:
            self.key = Fernet.generate_key()
            with open('encryption_key.key', 'wb') as key_file:
                key_file.write(self.key)
        
        self.fernet = Fernet(self.key)
    
    def anonymize_name(self, name, patient_id):
        return f"ANON_{patient_id:04d}"
    
    def anonymize_contact(self, contact):
        if len(contact) >= 4:
            return "XXX-XXX-" + contact[-4:]
        return "XXX-XXX-XXXX"
    
    def encrypt_data(self, data):
        """Encrypt data for reversible anonymization"""
        if data is None:
            return None
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data for authorized access"""
        if encrypted_data is None:
            return None
        try:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        except:
            return "Decryption failed"
    
    def apply_reversible_anonymization(self, patient_data):
        """Apply reversible encryption instead of permanent masking"""
        anonymized_data = patient_data.copy()
        
        # Store original data encrypted
        anonymized_data['encrypted_name'] = self.encrypt_data(patient_data['name'])
        anonymized_data['encrypted_contact'] = self.encrypt_data(patient_data['contact'])
        
        # Also apply regular anonymization for display
        anonymized_data['anonymized_name'] = self.anonymize_name(patient_data['name'], patient_data['patient_id'])
        anonymized_data['anonymized_contact'] = self.anonymize_contact(patient_data['contact'])
        
        return anonymized_data
    
    def reveal_original_data(self, patient_data):
        """Decrypt and reveal original data (admin only)"""
        revealed_data = patient_data.copy()
        
        if 'encrypted_name' in patient_data and patient_data['encrypted_name']:
            revealed_data['original_name'] = self.decrypt_data(patient_data['encrypted_name'])
        if 'encrypted_contact' in patient_data and patient_data['encrypted_contact']:
            revealed_data['original_contact'] = self.decrypt_data(patient_data['encrypted_contact'])
        
        return revealed_data