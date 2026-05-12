from uuid import uuid4  # Добавьте этот импорт
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse  # Добавьте этот импорт
from pydantic import ValidationError

from app.models.schemas import (
    AnalyzeRequest,
    JobAnalysis,
    ChatRequest,
    SearchJobsRequest,
)
from app.services.analyzer import (
    analyze_job_function,
    search_jobs,
    chat_with_job_streaming,
)


router = APIRouter()

@router.post("/analyze-job", response_model=JobAnalysis)
async def analyze_job(request: AnalyzeRequest):
    try:
        return await analyze_job_function(request)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors())


@router.post("/search-jobs")
async def search_jobs_endpoint(request: SearchJobsRequest):
    result = search_jobs(query=request.query, location=request.location)
    return {"jobs": result}


@router.post("/chat-about-job/stream")
async def chat_streaming(request: ChatRequest):
    session_id = request.session_id or str(uuid4())

    gen = chat_with_job_streaming(request.message, session_id)

    return StreamingResponse(
        gen, media_type="text/event-stream", headers={"x-session-id": session_id}
    )
