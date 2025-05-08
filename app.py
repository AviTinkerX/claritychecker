import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Clarity Checker", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>Clarity Checker</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #4A5568;'>Upload your team's data and visualize clarity.</h3>", unsafe_allow_html=True)

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
            "Average Call Handle Time (seconds)": 600,
            "Sampling Rate (%)": 'Undefined'
        }

        # Calculate key metrics
        total_customers = len(df)
        if total_customers > 0:
            total_responded = df['Survey_Responded'].sum()
            sampling_rate = (total_responded / total_customers) * 100
        else:
            sampling_rate = 0.0

        # Check if Sampling Rate Goal is Defined
        if goals["Sampling Rate (%)"] == 'Undefined':
            st.markdown("""
                <div style='background-color:#ffcccc; color:#990000; padding:10px; border-radius:5px; margin-bottom:15px;'>
                    <strong>⚠️ Recognition Integrity Breach Detected:</strong> 
                    No defined Sampling Rate Goal. This opens the door to data manipulation, cherry-picking, and misleading performance evaluations. 
                    Leaders need to set clear sampling goals to prevent false recognitions and ensure real performance is rewarded.
                </div>
            """, unsafe_allow_html=True)

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
            lambda x: '❌ Breach (No Sampling Goal)' if goals["Sampling Rate (%)"] == 'Undefined' else (
                '❌ Breach' if x['Rep Sampling Rate (%)'] < 40 else '✅ Clear'
            ),
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
                'Customer Satisfaction (%)',
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
                'Undefined',
                goals["Customer Satisfaction (%)"],
                goals["First Call Resolution (%)"],
                goals["Average Call Handle Time (seconds)"]
            ]
        })

        # Render the bar chart visualization
        fig = go.Figure()

        for index, row in summary_df.iterrows():
            bar_color = "green"
            if row['Metric'] == 'Average Call Handle Time (seconds)':
                bar_color = "green" if row['Current Value'] < row['Goal'] else "red"
            else:
                bar_color = "red" if row['Current Value'] < float(row['Goal']) else "green"

            fig.add_trace(go.Bar(
                x=[row['Current Value']],
                y=[f"{row['Metric']} ({row['Current Value']} / {row['Goal']})"],
                orientation='h',
                marker=dict(color=bar_color),
                text=f"{row['Current Value']} / {row['Goal']}",
                textposition='auto'
            ))

        # Layout settings
        fig.update_layout(
            title="<b>Organizational Clarity Dashboard</b>",
            height=600,
            width=800,
            margin=dict(l=50, r=50, t=50, b=50),
            font=dict(size=14, color="white"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title='Value', showgrid=False),
            yaxis=dict(showgrid=False)
        )

        # Display the dashboard
        st.plotly_chart(fig, use_container_width=True)
