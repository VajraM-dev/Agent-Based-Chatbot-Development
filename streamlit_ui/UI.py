import streamlit as st
import requests
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(".env.dev"))
# API base URL
API_BASE_URL = os.environ.get("FAST_API_ENDPOINT")  # Change this to your FastAPI server URL if different
API_KEY = os.environ.get("FAST_API_AUTH_KEY")  # Replace with your actual API key

# Function to authenticate API calls
def authenticated_api_call(endpoint, method="GET", data=None, files=None):
    headers = {"X-API-Key": API_KEY}
    url = f"{API_BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if files:
                response = requests.post(url, headers=headers, files=files)
            else:
                response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.json()['detail']}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None

# Set up the Streamlit app
st.title("Logistics Chatbot")

# Initialize session state
if "config" not in st.session_state:
    st.session_state.config = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to handle chatbot response
def get_chatbot_response(prompt):
    response = authenticated_api_call(
        "/get_response", method="POST", data={"query": prompt, "config": st.session_state.config}
    )
    if response:
        return response["result"]
    return "Error in getting response from the chatbot."

# Sidebar for session controls
st.sidebar.title("Session Controls")

# 1. Start Session Button
if st.session_state.config is None:
    if st.sidebar.button("Start Session"):
        session_data = authenticated_api_call("/getSessionConfig")
        if session_data:
            st.session_state.config = session_data
            st.success("Session started successfully!")
            st.session_state.messages.append({"role": "system", "content": "Session started."})

# 2. Delete Conversation Button (Separate)
if st.session_state.config:
    if st.sidebar.button("Delete Conversation"):
        delete_response = authenticated_api_call(
            "/clear_session_history", method="POST", data={"config": st.session_state.config}
        )
        if delete_response:
            st.success("Conversation deleted successfully!")
            st.session_state.config = None
            st.session_state.messages = []

if st.session_state.config:
    st.sidebar.title("Upload a File")

    # Ensure file upload status is tracked
    if "file_uploaded" not in st.session_state:
        st.session_state.file_uploaded = False

    uploaded_file = st.sidebar.file_uploader("Upload your document (PDF or DOCX):", type=["pdf", "docx"])

    # Handle file upload only if it hasn't been processed
    if uploaded_file and not st.session_state.file_uploaded:
        with st.spinner("Uploading file..."):
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            upload_response = authenticated_api_call("/upload/", method="POST", files=files)

            if upload_response:
                st.sidebar.success("File uploaded and processed successfully!")
                st.session_state.file_uploaded = True  # Mark the file as uploaded
                # Optionally store the response if needed
                st.session_state.file_upload_response = upload_response
            else:
                st.sidebar.error("Failed to upload or process the file.")

# Display the chat history
if st.session_state.config:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input box
    if prompt := st.chat_input("Your message..."):
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get assistant's response and add it to session state
        response = get_chatbot_response(prompt)
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.write("Please start a new session using the 'Start Session' button in the sidebar.")
