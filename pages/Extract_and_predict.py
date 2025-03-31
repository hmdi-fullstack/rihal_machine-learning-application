import streamlit as st
import pandas as pd
import pdfplumber
import re
import folium
from streamlit_folium import folium_static
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

# ✅ Configure the Streamlit app settings
st.set_page_config(
    page_title="Crime Report Extraction and Category prediction", layout="wide")

# ✅ Initialize session state to store crime data
if "crime_data" not in st.session_state:
    st.session_state.crime_data = pd.DataFrame()

# ✅ Function to train and load the model


@st.cache(allow_output_mutation=True)
def train_model():
    # 📌 Ensure the dataset contains "Descript" (crime description) and "Category" (crime type)
    df = pd.read_csv("./Competition_Dataset.csv")

    # Define input features (crime descriptions) and target labels (crime categories)
    X = df["Descript"]
    y = df["Category"]

    # Split data into training and testing sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Create a text classification pipeline using TF-IDF Vectorizer and Naive Bayes classifier
    model = make_pipeline(TfidfVectorizer(), MultinomialNB())

    # Train the model
    model.fit(X_train, y_train)

    return model


# Load the trained model
model = train_model()

# ✅ Function to extract information from the crime report PDF


def extract_info(text):
    # Helper function to find text using regex
    def find(pattern):
        match = re.search(pattern, text)
        return match.group(1) if match else "Not specified"

    # Helper function to extract numerical values (latitude, longitude)
    def find_float(pattern):
        match = re.search(pattern, text)
        return float(match.group(1)) if match else None

    # Extract the detailed crime description
    description = find(r'Detailed Description:\s*(.+)')

    return {
        "Report Number": find(r'Report Number:\s*(\d{4}-\d+)'),
        "Date & Time": find(r'Date & Time:\s*([\d-]+\s[\d:]+)'),
        "Reporting Officer": find(r'Reporting Officer:\s*(.+)'),
        "Incident Location": find(r'Incident Location:\s*(.+)'),
        "Latitude": find_float(r'Coordinates:\s*\(([-\d.]+),'),
        "Longitude": find_float(r'Coordinates:\s*\([-\d.]+,\s*([-\d.]+)\)'),
        "Detailed Description": description,
        "Predicted Category": model.predict([description])[0] if description != "Not specified" else "Unknown",
        "Police District": find(r'Police District:\s*(.+)'),
        "Resolution": find(r'Resolution:\s*(.+)'),
        "Suspect Description": find(r'Suspect Description:\s*(.+)'),
        "Victim Information": find(r'Victim Information:\s*(.+)'),
    }


# ✅ Streamlit UI
st.title("📄 Crime Report Extraction & Classification")
st.write("Upload PDF police reports to extract, analyze crime details, and predict crime categories.")

# ✅ Upload PDF files
uploaded_files = st.file_uploader(
    "Upload PDF reports", type="pdf", accept_multiple_files=True
)

if uploaded_files:
    new_reports = []

    # Process each uploaded PDF file
    for uploaded_file in uploaded_files:
        with pdfplumber.open(uploaded_file) as pdf:
            # Extract text from all pages in the PDF
            text = "\n".join([page.extract_text()
                             for page in pdf.pages if page.extract_text()])
            # Extract crime details from the text
            extracted_data = extract_info(text)
            new_reports.append(extracted_data)

    # ✅ Add new extracted reports to session state (avoid duplicates)
    new_df = pd.DataFrame(new_reports)
    st.session_state.crime_data = pd.concat(
        [st.session_state.crime_data, new_df], ignore_index=True
    ).drop_duplicates()

# ✅ Display the extracted crime data as a table
st.subheader("Extracted Crime Reports")
st.dataframe(st.session_state.crime_data)

# ✅ Display a crime map
st.subheader("Crime Map")

if not st.session_state.crime_data.empty:
    # Initialize a folium map centered at a predefined location (San Francisco)
    crime_map = folium.Map(location=[37.77, -122.42], zoom_start=12)

    # Add markers for crime locations
    for _, row in st.session_state.crime_data.iterrows():
        if pd.notna(row["Latitude"]) and pd.notna(row["Longitude"]):
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=f"""
                <b>Report Number:</b> {row['Report Number']}<br>
                <b>Crime Category:</b> {row['Predicted Category']}<br>
                <b>Location:</b> {row['Incident Location']}
                """,
                icon=folium.Icon(color="red", icon="info-sign"),
            ).add_to(crime_map)

    # Render the map in Streamlit
    folium_static(crime_map)

# ✅ Button to clear the extracted reports table
if st.button("🗑️ Clear Table"):
    st.session_state.crime_data = pd.DataFrame()
    st.success("Table cleared!")

# ✅ Option to download the extracted data as a CSV file
if not st.session_state.crime_data.empty:
    csv = st.session_state.crime_data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "crime_reports.csv", "text/csv")
