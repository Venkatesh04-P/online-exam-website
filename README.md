# ExamSecure — Online Examination Website

## Requirements
- Python 3.10+
- A browser
- VS Code (recommended)

## Run on Windows
1. Extract the ZIP and open this folder in VS Code.
2. In Terminal, run:
   ```powershell
   py -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   py app.py
   ```
3. Open http://127.0.0.1:5000 in your browser.

The `exam.db` SQLite database is created automatically when the app starts.
Use `/admin/results` to view local demo submissions. This page has no admin login and must not be exposed publicly.

## Customize
- Edit the `QUESTIONS` list in `app.py` to change questions/options/answers.
- Change `EXAM_DURATION_MINUTES` in `app.py` to set the duration.
- Styling is in `static/style.css`.

## Important limitations
This is a local learning/demo project. The start page asks for a name and student ID but does not authenticate identity. Do not use for a real/high-stakes exam until it is connected to verified authentication, administrator login is added, and production security is configured. For deployment, set a strong `EXAM_SECRET_KEY` environment variable, disable debug mode, use HTTPS, and add server-side attempt/deadline enforcement and appropriate data protection.
