from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class Skill(BaseModel):
    name: str
    level: Literal["must_have", "nice_to_have"]
    why_important: str


class RedFlag(BaseModel):
    issue: str
    severity: Literal["low", "medium", "high"]


class JobAnalysis(BaseModel):
    job_title: str
    required_skills: List[Skill]
    seniority_level: Literal["junior", "middle", "senior"]
    main_tech_stack: List[str]
    red_flags: List[RedFlag]
    match_score: int = Field(
        ge=0,
        le=100,
        description="0=нет совпадений, 100=идеальное совпадение. Учитывай только технические навыки",
    )
    recommendation: str = Field(
        description="1-2 предложения: стоит ли подавать заявку и почему",
    )


class AnalyzeRequest(BaseModel):
    job_description: str
    your_skills: List[str] = [
        "Java",
        "Django",
        "FastAPI",
        "PostgreSQL",
        "Docker",
        "REST API",
    ]


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    your_skills: List[str] = [
        "Python",
        "Django",
        "FastAPI",
        "PostgreSQL",
        "Docker",
        "REST API",
    ]


class ChatResponse(BaseModel):
    reply: str
    session_id: str


class SearchJobsRequest(BaseModel):
    query: str
    location: str = None
