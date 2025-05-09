import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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
            "Sampling Rate (%)": "Undefined"
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
            lambda x: '❌ Breach' if goals["Sampling Rate (%)"] == "Undefined" or x['Rep Sampling Rate (%)'] < 40 else '✅ Clear',
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
                "Undefined",
                85,
                80,
                600
            ]
        })

        # Plotly Bar Chart
        st.markdown("## 📊 Clarity Dashboard")
        for index, row in summary_df.iterrows():
            color = 'green' if row['Current Value'] >= row['Goal'] else 'red'
            fig = go.Figure(go.Bar(
                x=[row['Current Value']],
                y=[row['Metric']],
                orientation='h',
                marker=dict(color=color),
                text=f"{row['Current Value']} / {row['Goal']}",
                textposition='inside'
            ))
            fig.update_layout(
                xaxis=dict(range=[0, max(row['Goal'] + 10, 1000)]),
                width=800,
                height=200,
                margin=dict(l=50, r=50, t=30, b=30)
            )
            st.plotly_chart(fig)

        st.success("✅ Analysis Complete")
