import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Clarity Checker™", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>Clarity Checker™</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #4A5568;'>Upload your team's data and visualize clarity like never before.</h3>", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("📤 Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Load the data
    df = pd.read_csv(uploaded_file)

    if df.empty:
        st.warning("The uploaded CSV file is empty.")
    else:
        # Define goals
        goals = {
            "Customer Satisfaction (%)": 85,
            "First Call Resolution (%)": 80,
            "Average Call Handle Time (s)": 600,
            "Sampling Rate (%)": 40
        }

        # Calculate key metrics
        total_customers = len(df)
        if total_customers > 0:
            total_responded = df['Survey_Responded'].sum()
            sampling_rate = (total_responded / total_customers) * 100
        else:
            sampling_rate = 0.0

        # Rep-level analysis
        rep_analysis = df.groupby('Rep_Name').agg(
            Survey_Responded_Count=('Survey_Responded', 'sum'),
            Calls_Handled=('Rep_Name', 'size'),
            Customer_Satisfaction_Avg_Score=('Customer_Satisfaction_Score', 'mean'),
            First_Call_Resolved_Rate=('First_Call_Resolved', lambda x: (x.str.lower() == 'yes').mean() * 100),
            Call_Handle_Time_Avg=('Call_Handle_Time', 'mean')
        ).reset_index()

        # Calculate Rep Sampling Rate
        rep_analysis['Rep Sampling Rate (%)'] = rep_analysis.apply(
            lambda row: (row['Survey_Responded_Count'] / row['Calls_Handled']) * 100 if row['Calls_Handled'] > 0 else 0,
            axis=1
        )

        # Identification of Recognition Integrity Breach
        rep_analysis['Recognition Integrity'] = rep_analysis.apply(
            lambda x: '❌ Breach' if x['Rep Sampling Rate (%)'] < goals["Sampling Rate (%)"] else '✅ Clear',
            axis=1
        )

        # Display the Rep Analysis Table
        st.markdown("### Representative Analysis")
        st.dataframe(rep_analysis[[
            'Rep_Name',
            'Rep Sampling Rate (%)',
            'Customer_Satisfaction_Avg_Score',
            'First_Call_Resolved_Rate',
            'Call_Handle_Time_Avg',
            'Recognition Integrity'
        ]])

        # Prepare a summary DataFrame
        summary_df = pd.DataFrame({
            'Metric': [
                'Sampling Rate (%)',
                'Average Customer Satisfaction (%)',
                'First Call Resolution (%)',
                'Average Call Handle Time (seconds)'
            ],
            'Current Value': [
                round(sampling_rate, 1),
                round(rep_analysis['Customer_Satisfaction_Avg_Score'].mean() * 100 / 5, 1),
                round(rep_analysis['First_Call_Resolved_Rate'].mean(), 1),
                round(rep_analysis['Call_Handle_Time_Avg'].mean(), 1)
            ],
            'Goal': [
                'Undefined' if sampling_rate == 0 else goals["Sampling Rate (%)"],
                goals["Customer Satisfaction (%)"],
                goals["First Call Resolution (%)"],
                goals["Average Call Handle Time (s)"]
            ]
        })

        # Render Visual Capitalist-style dashboard
        fig = go.Figure()

        # Loop through metrics and add to dashboard
        for index, row in summary_df.iterrows():
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=row['Current Value'],
                title={"text": f"{row['Metric']} - Goal: {row['Goal']}"},
                gauge={
                    'axis': {'range': [0, 100] if '%' in row['Metric'] else [0, 1000]},
                    'bar': {'color': "orange" if row['Current Value'] < goals.get(row['Metric'], 100) else "#4CAF50"},
                    'steps': [
                        {'range': [0, goals.get(row['Metric'], 100)], 'color': 'red'},
                        {'range': [goals.get(row['Metric'], 100), 100 if '%' in row['Metric'] else 1000], 'color': 'green'}
                    ]
                },
                domain={'x': [0, 0.5] if index % 2 == 0 else [0.5, 1], 'y': [0.5, 1] if index < 2 else [0, 0.5]}
            ))

        # Layout settings
        fig.update_layout(
            title="Clarity Checker Dashboard",
            height=600,
            width=800,
            margin=dict(l=50, r=50, t=50, b=50),
            font=dict(size=14, color="black")
        )

        # Display the dashboard
        st.plotly_chart(fig)

        # Option to download the visuals
        if st.button('Download Dashboard as PNG'):
            fig.write_image("/mnt/data/clarity_checker_dashboard_v2.png")
            st.markdown('[Download Image](sandbox:/mnt/data/clarity_checker_dashboard_v2.png)')
