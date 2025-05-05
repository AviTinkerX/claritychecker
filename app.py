import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Clarity Checker, layout="centered")
st.title("AI Clarity Checker")
st.subheader("Clarity Over Cosmetic — A Sample Reference Tool")

uploaded_file = st.file_uploader("📤 Upload the sample CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("📊 Preview of Uploaded Data:")
    st.dataframe(df)

    report = {}

    if 'Survey_Responded' in df.columns and 'Customer_Satisfaction_Score' in df.columns:
        st.markdown("### 📋 Detected: Customer Service Dataset")

        total_customers = len(df)
        total_responded = df['Survey_Responded'].sum()
        sampling_rate = (total_responded / total_customers) * 100

        report['Sampling Goal Presence'] = '❌ Failed (No visible target)' if sampling_rate < 30 else '✅ Passed'
        report['Sampling Size Adequacy'] = f"{'⚠️ Needs Review' if sampling_rate < 50 else '✅ Passed'} ({sampling_rate:.1f}% sampled)"

        responded_scores = df[df['Survey_Responded'] == 1]['Customer_Satisfaction_Score'].dropna()
        if not responded_scores.empty:
            avg_satisfaction = responded_scores.mean()
            satisfaction_result = '✅ Passed' if avg_satisfaction >= 4.25 else ('⚠️ Needs Review' if avg_satisfaction >= 3.5 else '❌ Failed')
            report['Customer Satisfaction Clarity'] = f"{satisfaction_result} (Avg: {avg_satisfaction:.2f})"
        else:
            report['Customer Satisfaction Clarity'] = '❌ Failed (No valid survey responses)'

        if 'First_Call_Resolved' in df.columns:
            fcr_rate = (df['First_Call_Resolved'] == 'Yes').sum() / total_customers * 100
            report['First Call Resolution'] = f"{'✅ Passed' if fcr_rate >= 80 else ('⚠️ Needs Review' if fcr_rate >= 65 else '❌ Failed')} ({fcr_rate:.1f}%)"

        if 'Call_Handle_Time' in df.columns:
            mean_handle_time = df['Call_Handle_Time'].mean()
            report['Call Handle Time Clarity'] = f"{'⚠️ Needs Review' if mean_handle_time > 600 else '✅ Passed'} (Avg: {mean_handle_time:.0f}s)"
            report['Time Format Usability'] = '❌ Failed (Time in seconds, not frontline-friendly)'

        if 'Recognition_Awarded' in df.columns:
            rep_group = df[df['Survey_Responded'] == 1].groupby('Rep_Name').agg({
                'Survey_Responded': 'sum',
                'Customer_Satisfaction_Score': 'mean',
                'Recognition_Awarded': 'first'
            }).reset_index()
            total_per_rep = df.groupby('Rep_Name').size().reset_index(name='Total_Customers')
            merged = pd.merge(rep_group, total_per_rep, on='Rep_Name')
            merged['Sample Size (%)'] = (merged['Survey_Responded'] / merged['Total_Customers']) * 100

            flagged = merged[(merged['Recognition_Awarded'] == 'Yes') & (merged['Sample Size (%)'] < 30)]
            if not flagged.empty:
                report['⚠️ Recognition Integrity'] = '❌ Recognition awarded with <30% sampling — potential manipulation or cosmetic pattern detected.'
            else:
                report['⚠️ Recognition Integrity'] = '✅ Recognition distribution appears sampling-aligned.'

    else:
        st.warning("Unrecognized format. Ensure your CSV contains: Survey_Responded, Customer_Satisfaction_Score, Rep_Name, and Recognition_Awarded.")

    if report:
        st.markdown("### ✅ Clarity Over Cosmetic™ Report")
        st.dataframe(pd.DataFrame(list(report.items()), columns=['Check Area', 'Result']))
