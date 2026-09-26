# Customer Feedback Sentiment Analyzer

A full-stack Python application that uses Streamlit for the frontend, FastAPI for the backend, SQLite for persistence, and Google Gemini for sentiment analysis.

## Project structure

```text
customer-feedback-analyzer/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   └── ai_service.py
├── frontend/
│   ├── __init__.py
│   └── app.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── feedback.db
└── README.md
```

## 1. Create and activate a virtual environment

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure environment variables

Copy the example file and add your Gemini API key:

```bash
cp .env.example .env
```

Then update `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
```

## 4. Start the FastAPI backend

```bash
fastapi dev backend/main.py
```

The API docs will be available at:

```text
http://127.0.0.1:8000/docs
```

## 5. Start the Streamlit frontend

In a second terminal:

```bash
streamlit run frontend/app.py
```

Then open the local Streamlit URL shown in the terminal.

## Example API request

### POST /analyze

```json
{
  "review": "The product is excellent and very easy to use."
}
```

### Response

```json
{
  "review": "The product is excellent and very easy to use.",
  "sentiment": "Positive",
  "explanation": "The customer expresses satisfaction with the product."
}
```

## Data flow

The app follows this flow:

```text
Streamlit -> FastAPI -> Pydantic validation -> Gemini AI -> SQLite
```

- Streamlit sends the customer review to the FastAPI `/analyze` endpoint.
- FastAPI validates the request using Pydantic.
- The backend passes the review to the Gemini AI service.
- Gemini returns a sentiment and explanation.
- The frontend displays the result.
- When the user saves it, Streamlit sends the already-analyzed result to `/feedback`, which stores it in SQLite.

## Notes

- The Gemini API key is loaded from `.env` and never hardcoded into source files.
- SQLite data is stored in the project root as `feedback.db`.
- The app never calls Gemini directly from Streamlit or SQLite directly from the frontend.

## Backend Run
cd /Users/vijay/Desktop/CustomerFeedBack_Analyzer
source .venv/bin/activate
fastapi dev backend/main.py


## Frontend Run
cd /Users/vijay/Desktop/CustomerFeedBack_Analyzer
source .venv/bin/activate
streamlit run frontend/app.py

