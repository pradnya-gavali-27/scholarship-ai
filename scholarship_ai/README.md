# Scholarship AI (Flask starter project)

A beginner-friendly scholarship guidance website with:
- responsive landing page
- general document checklist based on optional profile choices
- chatbot with a local fallback response
- optional OpenAI API integration
- reminders to verify scheme requirements from official sources

## 1. Install Python
Use Python 3.10+ if possible.

## 2. Create and activate a virtual environment

Windows:
```powershell
py -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 4. Configure environment variables
Copy `.env.example` to `.env`. Set a random `FLASK_SECRET_KEY`.
To enable AI-generated answers, add your own `OPENAI_API_KEY`. API usage may cost money.
Without an API key, the chatbot uses simple built-in guidance responses.

## 5. Run the website
```bash
python app.py
```
Open http://127.0.0.1:5000 in your browser.

## Important limitations
- This is a learning/demo project, not an official scholarship portal.
- Document suggestions are generic and may not match a particular scheme.
- It does not verify eligibility, submit applications, or check live deadlines.
- Before publishing, connect to current official scheme data and show the source and last-verified date.
- Do not collect or store full Aadhaar numbers, OTPs, passwords, or bank account numbers.
- Do not upload private documents to an AI API without explicit consent and a privacy review.
- For production, turn off Flask debug mode and configure secure deployment settings.
