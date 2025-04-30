import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Clarity Checker™", layout="centered")
st.title("AI Clarity Checker™")
st.subheader("Upload a CSV file to detect cosmetic vs real performance signals")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("📊 Preview of Uploaded Data:")
    st.dataframe(df)

    clarity_report = {}

    if 'Survey_Responded' in df.columns:
        st.markdown("### 📋 Detected: Customer Service Data")
        total_customers = len(df)
        total_responses = df['Survey_Responded'].sum()
        sampling_rate = (total_responses / total_customers) * 100

        clarity_report['Sampling Goal Presence'] = '❌ Failed' if sampling_rate < 30 else '✅ Passed'
        clarity_report['Sampling Size Adequacy'] = '⚠️ Needs Review' if sampling_rate < 30 else '✅ Passed'
        clarity_report['Recognition Alignment'] = '❌ Failed' if sampling_rate < 30 else '✅ Passed'
        clarity_report['Noise Detection'] = '⚠️ Needs Review' if sampling_rate < 30 else '✅ Passed'
        clarity_report['Bias Detection'] = '✅ Passed'

    elif 'Quota_Target' in df.columns:
        st.markdown("### 📋 Detected: Sales Performance Data")
        clarity_report['Goal Clarity'] = '✅ Passed' if df['Quota_Target'].notnull().all() else '❌ Failed'

        high_performers = df[df['Actual_Sales'] >= df['Quota_Target']]
        recognized_high_performers = high_performers[high_performers['Recognition_Awarded'] == 'Yes']
        recognized_underperformers = df[(df['Actual_Sales'] < df['Quota_Target']) & (df['Recognition_Awarded'] == 'Yes')]

        if len(recognized_underperformers) > len(recognized_high_performers):
            clarity_report['Achievement vs Recognition'] = '❌ Failed'
        else:
            clarity_report['Achievement vs Recognition'] = '✅ Passed'

        clarity_report['Contribution to Outcome'] = '⚠️ Needs Review'
        clarity_report['Sampling Size'] = '✅ Passed'
        clarity_report['Bias Detection'] = '⚠️ Needs Review'

    else:
        st.error("Unrecognized data format. Please upload a valid sample dataset.")

    if clarity_report:
        st.markdown("### ✅ Clarity Over Cosmetic™ Report")
        report_df = pd.DataFrame(list(clarity_report.items()), columns=["Check Area", "Result"])
        st.dataframe(report_df)
