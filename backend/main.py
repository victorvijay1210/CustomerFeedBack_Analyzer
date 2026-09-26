from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.ai_service import analyze_sentiment
from backend.database import Feedback, create_db_and_tables, get_db
from backend.models import (
    FeedbackHistoryItem,
    FeedbackRequest,
    FeedbackSaveRequest,
    FeedbackSavedResponse,
    SentimentResponse,
)

app = FastAPI(
    title="Customer Feedback Sentiment Analyzer",
    description="AI-powered customer feedback sentiment analysis API",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Any, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": "Please enter customer feedback."},
    )


@app.on_event("startup")
def startup_event() -> None:
    create_db_and_tables()


@app.post("/analyze", response_model=SentimentResponse)
def analyze_feedback(feedback: FeedbackRequest) -> SentimentResponse:
    try:
        result = analyze_sentiment(feedback.review)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return SentimentResponse(
        review=feedback.review,
        sentiment=result["sentiment"],
        explanation=result["explanation"],
    )


@app.post("/feedback", response_model=FeedbackSavedResponse)
def save_feedback(payload: FeedbackSaveRequest, db: Session = Depends(get_db)) -> FeedbackSavedResponse:
    try:
        feedback_record = Feedback(
            review=payload.review.strip(),
            sentiment=payload.sentiment.strip(),
            explanation=payload.explanation.strip(),
        )
        db.add(feedback_record)
        db.commit()
        db.refresh(feedback_record)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error. Please try again.") from exc

    return FeedbackSavedResponse(message="Feedback saved successfully", id=feedback_record.id)


@app.get("/feedback", response_model=list[FeedbackHistoryItem])
def get_feedback(db: Session = Depends(get_db)) -> list[FeedbackHistoryItem]:
    records = db.query(Feedback).order_by(Feedback.created_at.desc()).all()
    return [
        FeedbackHistoryItem(
            id=record.id,
            review=record.review,
            sentiment=record.sentiment,
            explanation=record.explanation,
            created_at=record.created_at,
        )
        for record in records
    ]
