import mysql.connector
import sqlite3
from datetime import datetime
import hashlib

class DatabaseManager:
    def __init__(self, db_type='sqlite', db_name='hospital.db'):
        self.db_type = db_type
        self.db_name = db_name
        self.init_database()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def get_connection(self):
        if self.db_type == 'sqlite':
            return sqlite3.connect(self.db_name)
        else:
            return mysql.connector.connect(
                host="localhost",
                user="your_username",
                password="your_password",
                database=self.db_name
            )
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        
        # Create patients table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            diagnosis TEXT NOT NULL,
            anonymized_name TEXT,
            anonymized_contact TEXT,
            encrypted_name TEXT,
            encrypted_contact TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
        
        # Create logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT,
                action TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        ''')
        
        # Insert default users
        default_users = [
            ('admin', self.hash_password('admin123'), 'admin'),
            ('dr_bob', self.hash_password('doc123'), 'doctor'),
            ('alice_recep', self.hash_password('rec123'), 'receptionist')
        ]
        
        for user in default_users:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                    user
                )
            except:
                pass
        
        conn.commit()
        conn.close()
    
    def log_activity(self, user_id, role, action, details=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (user_id, role, action, details) VALUES (?, ?, ?, ?)",
            (user_id, role, action, details)
        )
        conn.commit()
        conn.close()

    def enforce_data_retention(self, retention_days=30):
        """Remove records older than retention period"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Delete logs older than retention period
        cursor.execute(
            "DELETE FROM logs WHERE timestamp < datetime('now', ?)",
            (f'-{retention_days} days',)
        )
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
    
        return deleted_count    