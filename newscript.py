# ================================
# Fitbit Data Dashboard with Streamlit
# ================================

import pandas as pd
import streamlit as st
import plotly.express as px

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    daily_activity = pd.read_csv("dailyActivity_merged.csv")
    daily_calories = pd.read_csv("dailyCalories_merged.csv")
    daily_intensities = pd.read_csv("dailyIntensities_merged.csv")
    daily_steps = pd.read_csv("dailySteps_merged.csv")
    sleep_day = pd.read_csv("sleepDay_merged.csv")
    heartrate = pd.read_csv("heartrate_seconds_merged.csv")
    hourly_steps = pd.read_csv("hourlySteps_merged.csv")
    weight = pd.read_csv("weightLogInfo_merged.csv")

    # Convert dates
    daily_activity["ActivityDate"] = pd.to_datetime(daily_activity["ActivityDate"])
    daily_calories["ActivityDay"] = pd.to_datetime(daily_calories["ActivityDay"])
    daily_intensities["ActivityDay"] = pd.to_datetime(daily_intensities["ActivityDay"])
    daily_steps["ActivityDay"] = pd.to_datetime(daily_steps["ActivityDay"])
    sleep_day["SleepDay"] = pd.to_datetime(sleep_day["SleepDay"])
    heartrate["Time"] = pd.to_datetime(heartrate["Time"])
    hourly_steps["ActivityHour"] = pd.to_datetime(hourly_steps["ActivityHour"])
    weight["Date"] = pd.to_datetime(weight["Date"])

    return (daily_activity, daily_calories, daily_intensities, daily_steps,
            sleep_day, heartrate, hourly_steps, weight)


(daily_activity, daily_calories, daily_intensities, daily_steps,
 sleep_day, heartrate, hourly_steps, weight) = load_data()

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Fitbit Dashboard", layout="wide")

st.title("📊 Strava Fitness Dashboard")
st.markdown("Analyze your activity, sleep, calories, weight, and heart rate data interactively.")

# Sidebar Navigation
menu = st.sidebar.radio(
    "Select Analysis",
    ["Daily Activity", "Sleep Analysis", "Hourly Patterns", "Heart Rate", "Weight Log"]
)

# -------------------------------
# Daily Activity
# -------------------------------
if menu == "Daily Activity":
    st.header("📅 Daily Activity Overview")

    # Steps trend
    fig1 = px.line(daily_activity, x="ActivityDate", y="TotalSteps",
                   title="Daily Steps Over Time", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    # Steps vs Calories
    fig2 = px.scatter(daily_activity, x="TotalSteps", y="Calories",
                      title="Steps vs Calories Burned", trendline="ols")
    st.plotly_chart(fig2, use_container_width=True)

    # Correlation heatmap
    st.subheader("Correlation between Activity Metrics")
    corr = daily_activity[["TotalSteps", "TotalDistance", "Calories",
                           "VeryActiveMinutes", "FairlyActiveMinutes",
                           "LightlyActiveMinutes", "SedentaryMinutes"]].corr()
    st.dataframe(corr.style.background_gradient(cmap="Blues"))

# -------------------------------
# Sleep Analysis
# -------------------------------
elif menu == "Sleep Analysis":
    st.header("😴 Sleep Patterns")

    sleep_day["SleepHours"] = sleep_day["TotalMinutesAsleep"] / 60

    fig3 = px.histogram(sleep_day, x="SleepHours", nbins=20,
                        title="Distribution of Sleep Hours", marginal="box")
    st.plotly_chart(fig3, use_container_width=True)

    merged = pd.merge(sleep_day, daily_activity,
                      left_on="SleepDay", right_on="ActivityDate", how="inner")
    fig4 = px.scatter(merged, x="SleepHours", y="TotalSteps",
                      title="Sleep Duration vs Daily Steps", trendline="ols")
    st.plotly_chart(fig4, use_container_width=True)

# -------------------------------
# Hourly Patterns
# -------------------------------
elif menu == "Hourly Patterns":
    st.header("⏰ Hourly Activity Trends")

    hourly_steps["Hour"] = hourly_steps["ActivityHour"].dt.hour
    avg_steps = hourly_steps.groupby("Hour")["StepTotal"].mean().reset_index()

    fig5 = px.bar(avg_steps, x="Hour", y="StepTotal",
                  title="Average Steps by Hour of Day")
    st.plotly_chart(fig5, use_container_width=True)

# -------------------------------
# Heart Rate
# -------------------------------
elif menu == "Heart Rate":
    st.header("❤️ Heart Rate Analysis")

    available_dates = heartrate["Time"].dt.date.unique()
    selected_date = st.selectbox("Choose a date", available_dates)

    hr_day = heartrate[heartrate["Time"].dt.date == selected_date]

    fig6 = px.line(hr_day, x="Time", y="Value",
                   title=f"Heart Rate Throughout {selected_date}")
    st.plotly_chart(fig6, use_container_width=True)

# -------------------------------
# Weight Log
# -------------------------------
elif menu == "Weight Log":
    st.header("⚖️ Weight & BMI Trends")

    if weight.empty:
        st.warning("No weight log data available.")
    else:
        # Weight trend
        fig7 = px.line(weight, x="Date", y="WeightKg",
                       title="Weight Trend Over Time", markers=True)
        st.plotly_chart(fig7, use_container_width=True)

        # BMI trend
        fig8 = px.line(weight, x="Date", y="BMI",
                       title="BMI Trend Over Time", markers=True, color_discrete_sequence=["green"])
        st.plotly_chart(fig8, use_container_width=True)

        # Current stats
        latest_weight = weight.sort_values("Date", ascending=False).iloc[0]
        st.metric("Latest Weight (kg)", f"{latest_weight['WeightKg']:.1f}")
        st.metric("Latest BMI", f"{latest_weight['BMI']:.1f}")


