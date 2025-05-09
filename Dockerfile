# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /main

# Copy the current directory contents into the container
COPY . /main

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit default port
EXPOSE 8501

# Correct command to run Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
