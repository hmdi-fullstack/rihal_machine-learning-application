import streamlit as st

st.set_page_config(page_title="Crime Analysis Dashboard", layout="wide")

st.title("🚔 Crime Analysis Dashboard")
st.write("Navigate through the sidebar to explore crime patterns and predictions.")
st.write("Please click on load dataset, the program will load Competition_Dataset.csv file and transform it into a usable format and show you analysis of Dataset.")
st.sidebar.success("Select a page above ☝️")
