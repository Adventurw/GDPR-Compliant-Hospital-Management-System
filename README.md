# 🏥 GDPR-Compliant Hospital Management System

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.51+-red.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Completed-success.svg)

## 📋 Overview

A secure, GDPR-compliant Hospital Management System demonstrating the CIA Triad (Confidentiality, Integrity, Availability) in modern information systems. This project was developed as part of the Information Security course (CS-3002) to showcase practical implementation of security principles and privacy regulations.

### ✨ Key Features

- **🔐 Confidentiality**: Role-based access control (RBAC), data encryption, and anonymization
- **📝 Integrity**: Comprehensive audit logging and data validation
- **⚡ Availability**: Error handling, backup systems, and real-time monitoring
- **📊 GDPR Compliance**: Data minimization, consent management, and right to access
- **📈 Real-time Analytics**: Activity monitoring with interactive visualizations
- **🔄 Reversible Encryption**: Fernet encryption for authorized data access

## 🚀 Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
http://localhost:8501/

## 🛠️ Technology Stack

### Frontend
- **Streamlit**: Web application framework
- **Plotly**: Interactive data visualization
- **Pandas**: Data manipulation and display

### Backend
- **Python 3.8+**: Core programming language
- **SQLite**: Lightweight database (with MySQL support)
- **Cryptography**: Fernet encryption for data protection
- **Hashlib**: SHA-256 password hashing

### Security
- **Fernet Encryption**: Reversible data encryption
- **SHA-256**: Password hashing
- **RBAC**: Role-based access control
- **Session Management**: Secure user sessions

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Adventurw/GDPR-Compliant-Hospital-Management-System.git
cd GDPR-Compliant-Hospital-Management-System
```
2. **Install dependencies**
```bash
pip install -r requirements.txt
```
3. **Run the application**
```bash
streamlit run src/app.py
```
4. **Access the application**
```bash
Open your browser and navigate to http://localhost:8501
```
