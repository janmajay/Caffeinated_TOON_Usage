from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class Activity(BaseModel):
    id: int
    name: str
    timestamp: datetime
    metadata: Dict[str, str] = Field(default_factory=dict)
    duration_seconds: float

class Score(BaseModel):
    subject: str
    score: float
    max_score: float = 100.0
    date: datetime

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    roles: List[str]
    preferences: Dict[str, str]
    scores: List[Score]
    activities: List[Activity]
    bio: str
    created_at: datetime
    updated_at: datetime

class DataPayload(BaseModel):
    users: List[UserProfile]
    version: str = "1.0.0"
    generated_at: datetime = Field(default_factory=datetime.now)
