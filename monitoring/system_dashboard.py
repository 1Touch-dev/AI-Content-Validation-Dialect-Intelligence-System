import os
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="AI Video Validation - System Dashboard", layout="wide")

st.title("📹 AI Video Validation - System Monitoring Dashboard")

base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
logs_file = os.path.join(base_dir, "logs", "inference_metrics.csv")
drift_file = os.path.join(base_dir, "logs", "drift_alert.log")

if not os.path.exists(logs_file):
    st.error("Telemetry data not found. Run validation pipelines to generate metrics.")
    st.stop()

# Load Telemetry
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(logs_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading telemetry: {e}")
    st.stop()

# System Totals
total_inferences = len(df)
pass_rate = (df['validation_status'] == 'PASS').mean() * 100
avg_conf = df['dialect_confidence'].mean()
avg_visual = df['content_match_score'].mean()
avg_time = df['processing_time_s'].mean()

st.markdown("---")
# Core Metrics Layout
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Validations", total_inferences)
with col2:
    st.metric("System Pass Rate", f"{pass_rate:.1f}%", delta=f"{pass_rate - 70:.1f}% vs Goal" if pass_rate < 70 else None, delta_color="normal")
with col3:
    st.metric("Avg Dialect Confidence", f"{avg_conf:.2f}")
with col4:
    st.metric("Avg Visual Matching", f"{avg_visual:.2f}")
with col5:
    st.metric("Avg Pipeline Speed", f"{avg_time:.2f}s")
    
st.markdown("---")

# Visualizations Map
colA, colB = st.columns(2)

with colA:
    st.subheader("Validation Decisions Distribution")
    fig_pie = px.pie(df, names='validation_status', color='validation_status', 
                     color_discrete_map={'PASS':'#2E8B57', 'FAIL':'#DC143C'}, hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)
    
with colB:
    st.subheader("System Dialect Predictions")
    fig_bar = px.histogram(df, x='dialect_prediction', color='validation_status',
                           color_discrete_map={'PASS':'#2E8B57', 'FAIL':'#DC143C'})
    st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("Confidence Trend Over Time")
# Smoothing out chronological line plot
fig_line = px.line(df, x='timestamp', y=['dialect_confidence', 'content_match_score'], 
                   labels={'value': 'Confidence Score', 'variable': 'Metric Stream'})
st.plotly_chart(fig_line, use_container_width=True)

# Drift Alerts System Status
st.markdown("---")
st.subheader("🚨 Model Health & Drift Alerts")

# Quick Drift Rule Check
if pass_rate < 50.0 or avg_conf < 0.85:
    st.error("**SYSTEM_DRIFT_DETECTED: MODEL_RETRAINING_RECOMMENDED = TRUE**")
    if os.path.exists(drift_file):
        with open(drift_file, 'r') as f:
            logs = f.readlines()[-5:]
            for log in logs:
                st.warning(log.strip())
else:
    st.success("**SYSTEM_MONITORING_ACTIVE = TRUE. Validation System is Stable.**")
    st.info("No categorical drift detected.")

st.markdown("---")
st.subheader("Raw Telemetry Feed")
st.dataframe(df.tail(10).sort_values("timestamp", ascending=False), use_container_width=True)
