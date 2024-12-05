from flask import Flask, render_template, request
from transformers import pipeline

# Initialize Flask app
app = Flask(__name__)

# Load the T5-small model for summarization
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")

# Function to summarize text with bullet points
def summarize_text(text):
    # Summarize the text with controlled output length
    summary = summarizer(text, max_length=150, min_length=80, length_penalty=1.0, do_sample=False)
    return summary[0]['summary_text']

# Function to convert summary to bullet points
def convert_to_bullet_points(text):
    points = text.split(".")  # Split summary by sentences
    points = [point.strip() for point in points if point]  # Clean up each point
    bullet_points = [f"• {point}" for point in points]  # Add bullet points
    return "\n".join(bullet_points)

# Route to render the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the form submission and display summary
@app.route('/summarize', methods=['POST'])
def summarize():
    # Get content from the form
    content = request.form['content']
    
    # Generate summary
    raw_summary = summarize_text(content)
    
    # Convert the summary into bullet points
    bullet_summary = convert_to_bullet_points(raw_summary)
    
    # Return the bullet-point summary on the page
    return render_template('index.html', summary=bullet_summary)

if __name__ == '__main__':
    app.run(debug=True)
