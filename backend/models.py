from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review: str = Field(..., min_length=1, description="Customer feedback text")

    @field_validator("review")
    @classmethod
    def validate_review(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Please enter customer feedback.")
        if len(cleaned) < 2:
            raise ValueError("Please enter customer feedback.")
        return cleaned


class SentimentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review: str
    sentiment: str
    explanation: str


class FeedbackSaveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review: str = Field(..., min_length=1)
    sentiment: str = Field(..., min_length=1)
    explanation: str = Field(..., min_length=1)


class FeedbackSavedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str
    id: int


class FeedbackHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    review: str
    sentiment: str
    explanation: str
    created_at: datetime
