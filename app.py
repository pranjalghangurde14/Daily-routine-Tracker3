import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
import os

# --- Title ---
st.title("📊 Daily Routine Tracker Dashboard")

# --- File Path ---
file_path = "data/routine_data.csv"

# --- Step 1: Create sample file if missing ---
if not os.path.exists(file_path):
    os.makedirs("data", exist_ok=True)
    sample_data = {
        "date": ["2025-07-01", "2025-07-01", "2025-07-02", "2025-07-02"],
        "activity": ["Sleep", "Work", "Sleep", "Leisure"],
        "hours_spent": [8, 9, 7, 3],
    }
    sample_df = pd.DataFrame(sample_data)
    sample_df.to_csv(file_path, index=False)
    st.success("✅ Sample data file created: 'data/routine_data.csv'")

# --- Step 2: Load DataFrame safely ---
try:
    # Show raw CSV if user wants
    if st.checkbox("🔍 Show Raw CSV Rows"):
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                st.text(row)

    # Load CSV
    df = pd.read_csv(file_path)

    # Clean column names (strip spaces)
    df.columns = df.columns.str.strip().str.lower()

    # Check for required columns
    required_cols = {"date", "activity", "hours_spent"}
    if not required_cols.issubset(df.columns):
        st.error(f"❌ CSV must have these columns: {required_cols}")
        st.stop()

    # Convert date column
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

except Exception as e:
    st.error(f"❌ Failed to read or process the CSV: {e}")
    st.stop()

# --- Step 3: Sidebar Filter ---
st.sidebar.header("📅 Filter Data")
unique_dates = df["date"].dropna().dt.date.unique()
selected_dates = st.sidebar.multiselect("Select Date(s)", unique_dates, default=unique_dates)

# --- Step 4: Filtered Data ---
filtered_df = df[df["date"].dt.date.isin(selected_dates)]

# --- Step 5: Summary Table ---
st.subheader("📌 Summary Table")
summary = filtered_df.groupby(["date", "activity"])["hours_spent"].sum().reset_index()
pivot = summary.pivot(index="date", columns="activity", values="hours_spent").fillna(0)
st.dataframe(pivot.style.format("{:.1f}"))

# --- Step 6: Pie Chart (Activity Breakdown) ---
st.subheader("🍕 Total Time Spent by Activity")
total_activity = filtered_df.groupby("activity")["hours_spent"].sum()
fig1, ax1 = plt.subplots()
ax1.pie(total_activity, labels=total_activity.index, autopct="%1.1f%%", startangle=90)
ax1.axis("equal")
st.pyplot(fig1)

# --- Step 7: Line Chart (Activity Trends Over Time) ---
st.subheader("📈 Activity Trend Over Time")
line_data = filtered_df.groupby(["date", "activity"])["hours_spent"].sum().unstack().fillna(0)
st.line_chart(line_data)

# --- Step 8: Daily Totals Bar Chart ---
st.subheader("⏱️ Daily Hours Balance")
daily_total = filtered_df.groupby("date")["hours_spent"].sum()
st.bar_chart(daily_total)

# --- Step 9: Highlight Imbalanced Days ---
st.markdown("🔍 **Days with <24 or >24 hours logged:**")
imbalanced = daily_total[daily_total != 24]
st.dataframe(imbalanced)
