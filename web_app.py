#!pip install -q google-generativeai flask python-dotenv

from flask import Flask, request, render_template_string
import os
from dotenv import load_dotenv
import google.generativeai as genai
import csv, time

# Load API key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("API key not found in .env")

genai.configure(api_key=API_KEY)

# Model call function
def call_model(prompt, model="gemini-1.5-flash", temperature=0.7, max_tokens=300):
    model_obj = genai.GenerativeModel(model)
    response = model_obj.generate_content(
        prompt,
        generation_config={"temperature": temperature, "max_output_tokens": max_tokens}
    )
    return response.text.strip()

# Map confidence to temperature
def temp_from_confidence(conf):
    return {"low": 0.3, "medium": 0.7, "high": 1.0}.get(conf.lower(), 0.7)

# AI functions
def answer_question(question, variant=1, temperature=0.7):
    prompts = [
        f"Q: {question}\nA: Provide a concise factual answer in 1–2 sentences.",
        f"You are a tutor. Answer: {question}. Explain simply and give one short example.",
        f"Answer: {question}. Provide a short answer, then 2 steps explaining it. Add confidence level."
    ]
    return call_model(prompts[variant-1], temperature=temperature)

def summarize_text(text, variant=1, temperature=0.7):
    prompts = [
        f"Summarize this in 2–3 sentences: {text}",
        f"Read: {text}. Give 5 bullet points and a one-sentence TL;DR.",
        f"Summarize this for a student in 3 sentences: {text}"
    ]
    return call_model(prompts[variant-1], temperature=temperature)

def generate_creative(prompt_text, variant=1, temperature=0.7):
    prompts = [
        f"Write a short story (200 words) about: {prompt_text}",
        f"Write a haiku poem about: {prompt_text}",
        f"Create a sci-fi scene (400 words) involving: {prompt_text}. Use dialogue and end with a twist."
    ]
    return call_model(prompts[variant-1], temperature=temperature)

# Feedback logging
def log_feedback(function, prompt_variant, user_input, assistant_output, helpful, comment, filename="feedback.csv"):
    header = ["timestamp","function","prompt_variant","user_input","assistant_output","helpful","comment"]
    write_header = not os.path.exists(filename)
    with open(filename, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"),
                         function, prompt_variant, user_input, assistant_output, helpful, comment])

# Flask app
app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Assistant</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f5f5f5; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
        .form-container { max-width: 700px; margin: 50px auto; }
        .feedback-container { background-color: #e9ecef; padding: 15px; border-radius: 10px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container form-container">
        <h1 class="text-center mb-4">🧠 AI Assistant</h1>
        <form method="post" class="bg-white p-4 rounded shadow">
            <div class="mb-3">
                <label class="form-label">Function:</label>
                <select name="fn" class="form-select">
                    <option value="qa">Answer a Question</option>
                    <option value="summ">Summarize Text</option>
                    <option value="creative">Generate Creative Content</option>
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label">Variant:</label>
                <select name="variant" class="form-select">
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label">Confidence:</label>
                <select name="confidence" class="form-select">
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                    <option value="high">High</option>
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label">Your Input:</label>
                <textarea name="user_input" rows="5" class="form-control"></textarea>
            </div>
            <button type="submit" class="btn btn-primary w-100">Run</button>
        </form>

        {% if output %}
        <div class="feedback-container">
            <h4 class="mt-3">Response</h4>
            <pre>{{ output }}</pre>

            <form method="post">
                <input type="hidden" name="fn" value="{{ fn }}">
                <input type="hidden" name="variant" value="{{ variant }}">
                <input type="hidden" name="user_input" value="{{ user_input }}">
                <input type="hidden" name="assistant_output" value="{{ output }}">
                <div class="mb-2">
                    <label class="form-label">Was this helpful?</label>
                    <select name="helpful" class="form-select">
                        <option value="yes">Yes</option>
                        <option value="no">No</option>
                    </select>
                </div>
                <div class="mb-2">
                    <label class="form-label">Any comment:</label>
                    <textarea name="comment" rows="2" class="form-control"></textarea>
                </div>
                <button name="feedback" value="1" class="btn btn-success">Submit Feedback</button>
            </form>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def index():
    output = ""
    fn = variant = user_input = ""
    if request.method == "POST":
        # Feedback submission
        if request.form.get("feedback"):
            log_feedback(
                function=request.form.get("fn"),
                prompt_variant=f"variant{request.form.get('variant')}",
                user_input=request.form.get("user_input"),
                assistant_output=request.form.get("assistant_output"),
                helpful=request.form.get("helpful"),
                comment=request.form.get("comment")
            )
            output = "✅ Feedback recorded. Thank you!"
        else:
            fn = request.form.get("fn")
            variant = int(request.form.get("variant", 1))
            user_input = request.form.get("user_input","").strip()
            conf = request.form.get("confidence", "medium")
            temperature = temp_from_confidence(conf)

            if fn == "qa":
                output = answer_question(user_input, variant, temperature)
            elif fn == "summ":
                output = summarize_text(user_input, variant, temperature)
            else:
                output = generate_creative(user_input, variant, temperature)

    return render_template_string(HTML, output=output, fn=fn, variant=variant, user_input=user_input)

if __name__ == "__main__":
    app.run(debug=True)
