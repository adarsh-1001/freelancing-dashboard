# smart_billing_dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

st.set_page_config(page_title="Month-wise Billing Dashboard", layout="wide", page_icon="📊")
st.title("📊 Month Wise Billing Analysis (2025-26)")

# ------------------------
# File upload
# ------------------------
uploaded_file = st.file_uploader("Upload Excel or CSV file", type=["xlsx","csv"])
if uploaded_file:

    # ------------------------
    # Read file
    # ------------------------
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, skiprows=5)
    else:
        df = pd.read_excel(uploaded_file, skiprows=5)

    # ------------------------
    # Clean column names
    # ------------------------
    def clean_col(c):
        return re.sub(r'\W+', '', str(c).lower())  # remove non-alphanumeric and lowercase

    df.columns = [clean_col(c) for c in df.columns]

    # ------------------------
    # Detect columns
    # ------------------------
    try:
        sr_col = [c for c in df.columns if 'sr' in c][0]
        month_col = [c for c in df.columns if 'month' in c][0]
        amount_col = [c for c in df.columns if 'amount' in c][0]
        df = df[[sr_col, month_col, amount_col]]
        df.columns = ['SrNo', 'Month', 'Amount']
    except IndexError:
        st.error("Could not detect required columns. Make sure your file has Sr No, Month, and Amount.")
        st.stop()

    # ------------------------
    # Clean Amount column
    # ------------------------
    df['Amount'] = df['Amount'].astype(str).str.replace(',','').astype(float)

    # Drop summary rows (like Total / Final Sales)
    df = df[pd.to_numeric(df['SrNo'], errors='coerce').notnull()]
    df = df.reset_index(drop=True)

    # ------------------------
    # Month filter
    # ------------------------
    months = df['Month'].unique()
    selected_months = st.multiselect("Select Months", options=months, default=list(months))
    df_filtered = df[df['Month'].isin(selected_months)]

    # ------------------------
    # Show table
    # ------------------------
    st.subheader("Cleaned Data")
    st.dataframe(df_filtered)

    # ------------------------
    # Summary metrics
    # ------------------------
    total_sales = df_filtered['Amount'].sum()
    credit_note = st.number_input("Credit Note Amount", value=2756778, step=1)
    final_sales = total_sales - credit_note

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Sales", f"{total_sales:,.0f}")
    col2.metric("📝 Credit Note", f"{credit_note:,.0f}")
    col3.metric("🏆 Final Sales", f"{final_sales:,.0f}")

    # ------------------------
    # Bar chart
    # ------------------------
    st.subheader("Month-wise Billing")
    plt.figure(figsize=(12,6))
    max_val = df_filtered['Amount'].max()
    colors = ["green" if x < max_val*0.5 else "orange" if x < max_val*0.8 else "red" for x in df_filtered['Amount']]
    sns.barplot(x='Month', y='Amount', data=df_filtered, palette=colors)
    plt.xticks(rotation=45)
    plt.ylabel("Amount")
    plt.xlabel("Month")
    plt.title("Month-wise Billing")
    st.pyplot(plt)

    # ------------------------
    # Trend line
    # ------------------------
    st.subheader("Sales Trend")
    st.line_chart(df_filtered.set_index('Month')['Amount'])

    # ------------------------
    # Download cleaned CSV
    # ------------------------
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Cleaned Data", csv, "cleaned_billing.csv", "text/csv")

else:
    st.info("Upload a CSV or Excel file to see the dashboard.")
