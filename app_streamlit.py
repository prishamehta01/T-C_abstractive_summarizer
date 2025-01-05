import streamlit as st
import requests

# URL of your Flask server
FLASK_URL = 'http://127.0.0.1:5000'

# Maximum allowed characters (aligned with T5's input token limit)
MAX_CHAR_LIMIT = 2000  # Approximately aligns with 512 tokens for T5

# Function to summarize text via Flask API
def summarize_text_via_flask(content, id_token):
    url = f"{FLASK_URL}/summarize"
    headers = {"Content-Type": "application/json"}
    payload = {
        "content": content,
        "idToken": id_token  # Include the ID token in the payload
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Function to get ID token from the URL query parameters
def get_id_token_from_url():
    query_params = st.query_params  # Retrieve the query parameters
    print(f"Full Query Params: {query_params}")  # Debug: print query params to verify
    id_token = query_params['idToken']  # Get 'idToken' parameter from the URL
    if id_token:
        print(f"Retrieved ID Token: {id_token}")  # Log the token for debugging
    return id_token if id_token else None

# Streamlit app
def main():
    # Retrieve the ID token from the URL (query string) if available
    if 'id_token' not in st.session_state:
        id_token = get_id_token_from_url()  # Try to retrieve from the URL
        if id_token:
            st.session_state['id_token'] = id_token  # Save it to session state
        else:
            st.write("You are not logged in. Please login first.")
            return

    # Get the ID token from session state
    id_token = st.session_state['id_token']
    print(f"ID Token in session state: {id_token}")  # Log the ID token from session state

    # Input section
    st.title("Text Summarizer")
    content = st.text_area("Enter text to summarize (Max 2000 characters):", height=200)

    # Character limit check
    if len(content) > MAX_CHAR_LIMIT:
        st.error(f"Input exceeds the maximum allowed length of {MAX_CHAR_LIMIT} characters. Please shorten your text.")
        return

    # Summarize button
    if st.button("Summarize"):
        if content and id_token:
            result = summarize_text_via_flask(content, id_token)  # Call Flask API for summarization
            if 'summary' in result:
                st.subheader("Summary:")
                # Display the summary inside a box with markdown for better styling
                st.markdown(f"<div style='background-color:#333333 ;color:white; padding: 15px; border-radius: 5px; font-size: 16px; border: 1px solid #ddd;'>{result['summary']}</div>", unsafe_allow_html=True)
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")
        else:
            st.error("Please provide both content and ensure the user is logged in.")

if __name__ == '__main__':
    main()
