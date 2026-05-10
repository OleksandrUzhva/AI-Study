import json
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from app.models.schemas import (
    AnalyzeRequest,
    JobAnalysis,
    ChatRequest,
    ChatResponse,
    SearchJobsRequest,
)
from app.services.analyzer import (
    analyze_job_function,
    compare_jobs_function,
    search_jobs,
)
from app.services.session import get_or_create_session, add_message, get_history
from app.config import settings
from openai import AsyncOpenAI

router = APIRouter()
client = AsyncOpenAI(api_key=settings.openai_api_key)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_job",
            "description": "Анализирует вакансию и оценивает соответствие кандидата",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_description": {"type": "string"},
                    "your_skills": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["job_description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_jobs",
            "description": "Сравнивает несколько вакансий по заданным критериям",
            "parameters": {
                "type": "object",
                "properties": {
                    "jobs": {"type": "array", "items": {"type": "string"}},
                    "criteria": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["jobs", "criteria"],
            },
        },
    },
]


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


@router.post("/chat-about-job", response_model=ChatResponse)
async def chat_about_job(request: ChatRequest):
    sid = get_or_create_session(request.session_id, request.your_skills)
    add_message(sid, "user", request.message)

    response = await client.chat.completions.create(
        model=settings.model,
        messages=get_history(sid),
        tools=TOOLS,
        tool_choice="auto",
    )

    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        if tool_call.function.name == "analyze_job":
            result = await analyze_job_function(AnalyzeRequest(**args))
            reply = json.dumps(result.model_dump(), ensure_ascii=False)
        elif tool_call.function.name == "compare_jobs":
            reply = await compare_jobs_function(**args)
        else:
            reply = "Не знаю как обработать этот запрос"
    else:
        reply = response.choices[0].message.content

    add_message(sid, "assistant", reply)
    return ChatResponse(reply=reply, session_id=sid)
