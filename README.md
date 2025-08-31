# AI-Helper-App (A simple Flask-based AI Assistant)

This project is a simple AI-powered assistant that can:
1. **Answer Questions**
2. **Summarize Text**
3. **Generate Creative Content** (with multiple variants)
4. **Collect User Feedback**

The assistant uses APIs (such as Gemini / OpenAI) for generating responses and `pandas` for managing feedback data.

---

## Project Structure

```
├── main.py             # Main script (menu-driven assistant)
├── feedback.csv        # Stores user feedback
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## Installation

1. **Clone this project** or download the source code.
2. Make sure you have **Python 3.8+** installed.
3. Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Run the assistant with:

```bash
python main.py
```

You will be prompted with a menu to:
- Answer a question
- Summarize text
- Generate creative content (choose from variants)
- Exit

---

## Feedback Collection

- User feedback is stored in `feedback.csv`.
- You can analyze it using:

```python
import pandas as pd
df = pd.read_csv("feedback.csv")
print(df.tail())
```

---

## Configuration

If you’re using the **Gemini API**, store your API key in a `.env` file:

```
GEMINI_API_KEY=your_api_key_here
```

Then load it in your script using `dotenv`.

---

## Requirements

See [requirements.txt](requirements.txt).

---

## Future Enhancements
- Add confidence scoring
- Improve creative variants
- Visualize feedback with charts
- Extend to more tasks (translation, sentiment analysis, etc.)

---


Developed by **Manas Upadhyay**
