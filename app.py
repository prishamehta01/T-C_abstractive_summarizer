from flask import Flask, request, jsonify, render_template
from transformers import T5ForConditionalGeneration, T5Tokenizer

app = Flask(__name__, template_folder='templates')

# Load pre-trained T5 model and tokenizer for summarization
model_name = "t5-small"
model = T5ForConditionalGeneration.from_pretrained(model_name)
tokenizer = T5Tokenizer.from_pretrained(model_name)

# Function to summarize the input text
def summarize_text(text):
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = model.generate(inputs, max_length=150, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# Serve the HTML page at the root endpoint
@app.route('/')
def home():
    return render_template('index.html')  # This will render the index.html file

# Define an endpoint for summarization
@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    tc_text = data.get('tc_text', '')
    summary = summarize_text(tc_text)
    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(debug=True)
