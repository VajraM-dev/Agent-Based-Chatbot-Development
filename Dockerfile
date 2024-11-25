# Use the Python 3.10 base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies from requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the necessary ports
EXPOSE 8012 8501

# Set the default command to run both scripts
CMD ["sh", "-c", "python ./all_api.py & streamlit run streamlit_ui/UI.py"]