# Start with the official Python image
FROM python:3.11-slim



# Set the working directory inside the container
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential gcc g++ python3-dev
RUN pip install --upgrade pip


# Copy the requirements file into the container
COPY requirements.txt .


# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app folder into the container
COPY . .

# Expose the port that Streamlit will run on (default is 8501)
EXPOSE 8501

# Command to run the app
CMD ["streamlit", "run", "Home.py"]
