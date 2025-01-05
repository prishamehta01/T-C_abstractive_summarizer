import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, auth
from transformers import pipeline
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase Admin only if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate('./t-csummarization-a052e225838e.json')  # Use your actual Firebase credentials file
    firebase_admin.initialize_app(cred)

# Initialize HuggingFace Summarizer
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")

# Function to summarize text in chunks if it exceeds the token limit
def summarize_text_in_chunks(text, max_chunk_size=512):
    # Split the text into smaller chunks
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    
    # Summarize each chunk
    summarized_chunks = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=150, min_length=80, length_penalty=1.0, do_sample=False)
        summarized_chunks.append(summary[0]['summary_text'])
    
    # Combine all summarized chunks into one summary
    final_summary = " ".join(summarized_chunks)
    return final_summary

# Function to scrape the content from the URL
def scrape_content(url):
    try:
        # Send GET request to the URL
        response = requests.get(url)
        
        # If the request was successful, parse the content
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to get the main content of the page (this depends on the structure of the page)
            content = ''
            
            # Example: Scraping the main text from <article> or any <div> with class "content"
            article = soup.find('article')
            if article:
                content = article.get_text()
            else:
                # Fallback: try to find div with class 'content'
                content = soup.find('div', class_='content')
                if content:
                    content = content.get_text()
                else:
                    # If no article or content div, fall back to the whole text of the page
                    content = soup.get_text()
            
            return content.strip()
        else:
            return None
    except Exception as e:
        print(f"Error scraping content from {url}: {e}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

# Route to verify Firebase ID Token and get user details
@app.route('/verify_token', methods=['POST'])
def verify_token():
    try:
        # Retrieve the token from the request
        id_token = request.json.get('idToken')
        if not id_token:
            return jsonify({'error': 'ID Token is missing in the request body'}), 400

        # Verify the Firebase token
        decoded_token = auth.verify_id_token(id_token)
        user_uid = decoded_token['uid']

        # Construct the redirect URL
        redirect_url = f"http://localhost:8501/?idToken={id_token}"

        return jsonify({'redirect_url': redirect_url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Route to summarize text from URL or input text and return the result to the frontend
@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    content = data.get('content')
    id_token = data.get('idToken')
    url = data.get('url')  # The URL from which to scrape content

    if not content and not url:
        return jsonify({'error': 'Missing content or URL'}), 400
    if not id_token:
        return jsonify({'error': 'Missing ID token'}), 400

    try:
        # Verify ID Token with Firebase
        decoded_token = auth.verify_id_token(id_token)
        user_uid = decoded_token['uid']

        # If URL is provided, scrape the content
        if url:
            scraped_content = scrape_content(url)
            if scraped_content:
                content = scraped_content
            else:
                return jsonify({'error': 'Failed to scrape content from the provided URL'}), 400

        # Handle large content by breaking it into chunks and summarizing
        raw_summary = summarize_text_in_chunks(content)

        # Return the summary as a response
        return jsonify({'summary': raw_summary}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

CORS(app)

if __name__ == '__main__':
    app.run(debug=True)
