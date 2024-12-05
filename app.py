from flask import Flask, request, jsonify, render_template
from transformers import T5ForConditionalGeneration, T5Tokenizer

app = Flask(__name__, template_folder='templates')

# Load pre-trained T5 model and tokenizer for summarization
model_name = "t5-small"  # Instead of t5-large
  # Upgraded model for better performance
model = T5ForConditionalGeneration.from_pretrained(model_name)
tokenizer = T5Tokenizer.from_pretrained(model_name)

# Function to summarize the input text
def summarize_text(text, max_length=200, min_length=50):
    # Split input into chunks if too long
    max_input_length = 450  # Leave space for "summarize:" prefix
    chunks = [text[i:i + max_input_length] for i in range(0, len(text), max_input_length)]
    
    summaries = []
    for chunk in chunks:
        inputs = tokenizer.encode("summarize the key points of these Terms and Conditions: " + chunk,
                                  return_tensors="pt", max_length=512, truncation=True)
        summary_ids = model.generate(
            inputs,
            max_length=max_length,
            min_length=min_length,
            length_penalty=1.5,
            num_beams=6,
            no_repeat_ngram_size=3,
            early_stopping=True
        )
        summaries.append(tokenizer.decode(summary_ids[0], skip_special_tokens=True))
    
    return " ".join(summaries)

# Serve the HTML page at the root endpoint
@app.route('/')
def home():
    return render_template('index.html')  # Render the updated index.html

# Define an endpoint for summarization
@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    tc_text = data.get('tc_text', '')
    summary_length = data.get('summary_length', 'detailed')  # Get user's choice for summary length

    if summary_length == 'short':
        max_len = 100
        min_len = 30
    else:
        max_len = 300
        min_len = 50

    summary = summarize_text(tc_text, max_length=max_len, min_length=min_len)
    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(debug=True)
