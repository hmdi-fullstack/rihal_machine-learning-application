import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
from folium import Marker
from streamlit_folium import folium_static

# ✅ Page Configuration
st.set_page_config(page_title="Crime Data Dashboard", layout="wide")

# ✅ Initialize Session State
if "data" not in st.session_state:
    st.session_state.data = None

# ✅ Load dataset function


def load_dataset():
    data = pd.read_csv(
        "../Competition_Dataset.csv", parse_dates=["Dates"])

    # 📌 Extract Date Information
    data["Year"] = data["Dates"].dt.year
    data["Month"] = data["Dates"].dt.month
    data["Hour"] = data["Dates"].dt.hour
    data["Day"] = data["Dates"].dt.date

    st.session_state.data = data


# ✅ Button to Load & Transform Data
if st.button("📂 Load and Transform Dataset"):
    load_dataset()
    st.success("Dataset loaded and transformed successfully!")

# ✅ Display analysis only if data is loaded
if st.session_state.data is not None:
    data = st.session_state.data  # Get the dataset

    # 📊 Crimes per Year
    st.subheader("📆 Crimes Per Year")
    crimes_per_year = data["Year"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=crimes_per_year.index,
                y=crimes_per_year.values, palette="magma")
    plt.xlabel("Year")
    plt.ylabel("Number of Crimes")
    st.pyplot(fig)

    # 📅 Crimes per Month
    st.subheader("📅 Crimes Per Month")
    crimes_per_month = data["Month"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=crimes_per_month.index,
                y=crimes_per_month.values, palette="coolwarm")
    plt.xlabel("Month")
    plt.ylabel("Number of Crimes")
    st.pyplot(fig)

    # 📊 Crimes per Day
    st.subheader("📅 Crimes Per Day")
    crimes_per_day = data["Day"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(12, 4))
    sns.lineplot(x=crimes_per_day.index, y=crimes_per_day.values, ax=ax)
    plt.xticks(rotation=45)
    plt.xlabel("Date")
    plt.ylabel("Number of Crimes")
    st.pyplot(fig)

    # ⏰ Crimes per Hour
    st.subheader("⏳ Crimes Per Hour")
    crimes_per_hour = data["Hour"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(x=crimes_per_hour.index,
                y=crimes_per_hour.values, palette="coolwarm")
    plt.xlabel("Hour of the Day")
    plt.ylabel("Number of Crimes")
    st.pyplot(fig)

    # 🏢 Crimes per Police District
    st.subheader("🚓 Crimes Per District")
    crimes_per_district = data["PdDistrict"].value_counts()
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(x=crimes_per_district.index,
                y=crimes_per_district.values, palette="viridis")
    plt.xticks(rotation=45)
    plt.xlabel("Police District")
    plt.ylabel("Number of Crimes")
    st.pyplot(fig)

    st.subheader("🔥 Crime Heatmap & Epicenters")
    crime_map = folium.Map(location=[data["Latitude (Y)"].mean(
    ), data["Longitude (X)"].mean()], zoom_start=12)

    # ✅ Add Heatmap Layer
    heat_data = data[['Latitude (Y)', 'Longitude (X)']
                     ].dropna().values.tolist()
    HeatMap(heat_data, radius=50).add_to(crime_map)

    # ✅ Identify Crime Epicenters
    epicenters = data.groupby(
        ["Latitude (Y)", "Longitude (X)"]).size().reset_index(name="count")
    epicenters = epicenters.sort_values(
        by="count", ascending=False).head(20)  # Top 20 high-crime zones

    # ✅ Add Markers for Crime Epicenters
    for _, row in epicenters.iterrows():
        Marker(
            location=[row["Latitude (Y)"], row["Longitude (X)"]],
            popup=f"""
                <b>Crime Epicenter</b><br>
                <b>Cases:</b> {row['count']}<br>
                <b>Coordinates:</b> ({row["Latitude (Y)"]}, {row["Longitude (X)"]})
            """,
            icon=folium.Icon(color="darkred", icon="exclamation-triangle")
        ).add_to(crime_map)

    folium_static(crime_map)

else:
    st.warning("Please load the dataset first.")
