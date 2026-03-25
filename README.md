# LexSimply — AI Legal Document Simplifier

Turn complex legal contracts into simple, understandable insights in seconds.

---

## Overview

LexSimply is an AI-powered legal assistant that simplifies complex legal documents into plain English.
It helps users understand contracts by extracting key clauses, identifying risks, explaining legal jargon, and providing actionable insights.

Built using Streamlit, LangChain, and Gemini API, this app delivers an interactive and user-friendly experience with secure authentication and per-user chat history.

---

## Features

* Document Analysis
  Upload PDF, DOCX, or TXT files and receive structured insights

* Key Clause Extraction
  Identifies obligations, rights, penalties, and deadlines

* Risk Detection
  Highlights potentially risky or unusual clauses

* Legal Jargon Simplification
  Converts complex legal language into clear, plain English

* Conversational Q&A
  Ask follow-up questions about uploaded documents

* User Authentication
  Secure login system with hashed passwords and session handling

* Chat Memory
  Each user has isolated chat history stored locally

---

## Tech Stack

* Frontend/UI: Streamlit
* LLM Framework: LangChain
* Model: Google Gemini (langchain-google-genai)
* Backend Logic: Python
* Authentication: Custom SHA-256 + salt
* Document Parsing: pypdf, python-docx

---

## Project Structure

```
LexSimply/
│
├── app.py                # Main Streamlit app
├── main.py               # LLM logic and document processing
├── auth.py               # Authentication and user storage
├── login_ui.py           # Login/signup UI
├── prompts.py            # LLM prompt templates
├── requirements.txt      # Dependencies
├── .gitignore
├── users.json            # Local user storage (ignored in Git)
└── chat_histories/       # Per-user chat history (ignored in Git)
```

---

## Installation (Local Setup)

1. Clone the repository

```
git clone https://github.com/your-username/LexSimply-AI.git
cd LexSimply-AI
```

2. Create a virtual environment

```
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux
```

3. Install dependencies

```
pip install -r requirements.txt
```

4. Add environment variable
   Create a `.env` file:

```
GOOGLE_API_KEY=your_api_key_here
```

5. Run the app

```
streamlit run app.py
```

---

## Deployment (Streamlit Cloud)

1. Push your project to GitHub

2. Go to Streamlit Community Cloud

3. Deploy using:

   * Repository: your repo
   * Branch: main
   * File: app.py

4. Add secrets in Streamlit Cloud:

```
GOOGLE_API_KEY = "your_api_key_here"
```

---

## Security Notes

* API keys are not stored in the repository
* `.env`, `users.json`, and `chat_histories/` are ignored using `.gitignore`
* Passwords are hashed using SHA-256 with salt
* Chat history is isolated per user

---

## Limitations

* Local file-based storage is not persistent in cloud deployments
* Not intended to replace professional legal advice
* Performance depends on LLM response time

---

## Future Improvements

* Database integration for persistent user data
* Role-based access control
* Document version comparison
* Export reports (PDF / DOCX)
* Multi-language support

---

## Disclaimer

This application provides simplified explanations of legal documents and is not a substitute for professional legal advice. Always consult a licensed lawyer before making legal decisions.

---

## Author

Subasri B
