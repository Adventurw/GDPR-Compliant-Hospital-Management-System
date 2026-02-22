import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

class ActivityVisualization:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_activity_data(self):
        conn = self.db.get_connection()
        logs_df = pd.read_sql("SELECT * FROM logs ORDER BY timestamp DESC", conn)
        conn.close()
        return logs_df
    
    def plot_daily_activity(self):
        logs_df = self.get_activity_data()
        
        if logs_df.empty:
            st.warning("No activity data available")
            return
        
        # Convert timestamp to datetime
        logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
        logs_df['date'] = logs_df['timestamp'].dt.date
        
        # Group by date and action
        daily_activity = logs_df.groupby(['date', 'action']).size().reset_index(name='count')
        
        # Create stacked bar chart
        fig = px.bar(daily_activity, 
                    x='date', 
                    y='count', 
                    color='action',
                    title='Daily User Activities',
                    labels={'count': 'Number of Actions', 'date': 'Date'})
        
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_role_activity(self):
        logs_df = self.get_activity_data()
        
        if logs_df.empty:
            return
        
        # Group by role and action
        role_activity = logs_df.groupby(['role', 'action']).size().reset_index(name='count')
        
        # Create pie chart for role distribution
        role_dist = logs_df['role'].value_counts()
        fig = px.pie(role_dist, 
                    values=role_dist.values, 
                    names=role_dist.index,
                    title='Activity Distribution by Role')
        
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_action_timeline(self):
        logs_df = self.get_activity_data()
        
        if logs_df.empty:
            return
        
        # Create timeline of actions
        logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
        logs_df['hour'] = logs_df['timestamp'].dt.hour
        
        hourly_activity = logs_df.groupby('hour').size().reset_index(name='count')
        
        fig = px.line(hourly_activity, 
                     x='hour', 
                     y='count',
                     title='Activity Timeline (by Hour)',
                     markers=True)
        
        st.plotly_chart(fig, use_container_width=True)