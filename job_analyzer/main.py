from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError
from typing import List, Literal, Optional
from dotenv import load_dotenv
from openai import AsyncOpenAI
import os
import json
import uuid
from uuid import uuid4

load_dotenv()
app = FastAPI()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
sessions: dict[str, list[dict[str, str]]] = {} 
MAX_HISTORY = 20 # максимум сообщений в истории


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
        "Python",
        "Django",
        "FastAPI",
        "PostgreSQL",
        "Docker",
        "REST API",
    ]


class SearchJobsRequest(BaseModel):
    query: str
    location: str = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None 


class ChatResponse(BaseModel): 
    reply: str 
    session_id: str


async def analyze_job_function(request: AnalyzeRequest):
    """Helper function for analyzing a job posting."""

    prompt = f"""Проанализируй вакансию и оцени соответствие кандидата.
            Навыки кандидата: {', '.join(request.your_skills)}
            Вакансия: {request.job_description}"""

    response = await client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """Ты опытный технический рекрутер. Анализируй вакансии и формируй вывод в виде объекта JobAnalysis с такими полями:
                - job_title: краткий заголовок вакансии
                - required_skills: список объектов Skill, где каждый объект содержит:
                  name, level (must_have или nice_to_have), why_important
                - main_tech_stack: основные технологии проекта
                - red_flags: список объектов RedFlag, где каждый объект содержит:
                  issue и severity (low, medium или high)
                  Если тревог нет — возвращай пустой список.
                - match_score: число 0-100 насколько навыки кандидата совпадают с требованиями
                - recommendation: короткая рекомендация, стоит ли подаваться на эту вакансию
                """,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_format=JobAnalysis,
    )
    return response.choices[0].message.parsed


async def compare_jobs_function(jobs: List[str], criteria: List[str]):
    """Helper function for comparing multiple jobs."""
    prompt = f"""Сравни следующие вакансии по заданным критериям.

Вакансии:
{chr(10).join(f"{i+1}. {job}" for i, job in enumerate(jobs))}

Критерии для сравнения:
{chr(10).join(f"- {criterion}" for criterion in criteria)}

Дай подробное сравнение, укажи преимущества и недостатки каждой вакансии по каждому критерию."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


@app.post("/search-jobs")
async def search_jobs_endpoint(request: SearchJobsRequest):
    """
    Endpoint to search for jobs using AI-powered tool calling.
    The AI will decide whether to use the search function based on the query.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_jobs",
                "description": "Ищет вакансии по ключевым словам",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Поисковый запрос"},
                        "location": {"type": "string"},
                    },
                    "required": ["query"],
                },
            },
        }
    ]

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"Найди вакансии: {request.query}"
                + (f" в {request.location}" if request.location else ""),
            }
        ],
        tools=tools,
        tool_choice="auto",
    )

    # Handle tool calls
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            if tool_call.function.name == "search_jobs":
                args = json.loads(tool_call.function.arguments)
                result = search_jobs(**args)
                return {"jobs": result, "ai_decision": "Used search tool"}

    # If no tool calls, return AI's direct response
    return {
        "response": response.choices[0].message.content,
        "ai_decision": "Direct response",
    }


@app.post("/analyze-job", response_model=JobAnalysis)
async def analyze_job(request: AnalyzeRequest):
    try:
        return await analyze_job_function(request)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["body", "response"],
                    "msg": "Validation error while parsing AI response",
                    "type": "value_error",
                    "errors": exc.errors(),
                }
            ],
        )


@app.post("/chat-about-job", response_model=ChatResponse)
async def chat_about_job(request: ChatRequest):
    """
    Endpoint for chatting about jobs in free form.
    The AI will decide whether to call analyze_job or compare_jobs based on the message.
    """
    sid = request.session_id or str(uuid4()) 
    if sid not in sessions: 
        sessions[sid] = [{ "role": "system", "content": "Ты помощник по анализу вакансий" }] # Добавляем сообщение пользователя 
        sessions[sid].append({"role": "user", "content": request.message}) # Обрезаем если история слишком длинная 
        if len(sessions[sid]) > MAX_HISTORY: 
            sessions[sid] = [sessions[sid][0]] + sessions[sid][-MAX_HISTORY+1:]
            response = await client.chat.completions.create( model="gpt-4o-mini", messages=sessions[sid] ) 
            reply = response.choices[0].message.content 
            sessions[sid].append({"role": "assistant", "content": reply}) 
            return ChatResponse(reply=reply, session_id=sid)
        
    tools = [
        {
            "type": "function",
            "function": {
                "name": "analyze_job",
                "description": "Анализирует вакансию и оценивает соответствие кандидата",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_description": {
                            "type": "string",
                            "description": "Описание вакансии",
                        },
                        "your_skills": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Навыки кандидата",
                        },
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
                        "jobs": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Список описаний вакансий",
                        },
                        "criteria": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Критерии для сравнения",
                        },
                    },
                    "required": ["jobs", "criteria"],
                },
            },
        },
    ]

    session_id = request.session_id or str(uuid.uuid4())
    session = sessions.setdefault(session_id, [])
    session.append({"role": "user", "content": request.message})

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": request.message}],
        tools=tools,
        tool_choice="auto",
    )

    # Handle tool calls
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            if tool_call.function.name == "analyze_job":
                args = json.loads(tool_call.function.arguments)
                result = await analyze_job_function(AnalyzeRequest(**args))
                assistant_text = json.dumps(result, ensure_ascii=False)
                session.append({"role": "assistant", "content": assistant_text})
                return {
                    "session_id": session_id,
                    "analysis": result,
                    "ai_decision": "Used analyze_job tool",
                }
            elif tool_call.function.name == "compare_jobs":
                args = json.loads(tool_call.function.arguments)
                result = await compare_jobs_function(**args)
                session.append({"role": "assistant", "content": result})
                return {
                    "session_id": session_id,
                    "comparison": result,
                    "ai_decision": "Used compare_jobs tool",
                }

    assistant_text = response.choices[0].message.content
    session.append({"role": "assistant", "content": assistant_text})
    return {
        "session_id": session_id,
        "response": assistant_text,
        "ai_decision": "Direct response",
    }


def search_jobs(query: str, location: str = None):
    """
    Mock implementation of job search function.
    In a real application, you would integrate with a job search API like LinkedIn, etc.
    """
    # Mock data - replace with actual API call
    mock_jobs = [
        {
            "title": f"Python Developer - {query}",
            "company": "Tech Corp",
            "location": location or "Remote",
            "salary": "1000-1500 USD",
            "description": f"Looking for Python developer with experience in {query}",
        },
        {
            "title": f"Junior Python Engineer - {query}",
            "company": "Innovate Ltd",
            "location": location or "Spain",
            "salary": "1000-1500 USD",
            "description": f"Junior position requiring advanced {query} skills",
        },
    ]

    # Filter by location if provided
    if location:
        mock_jobs = [
            job for job in mock_jobs if location.lower() in job["location"].lower()
        ]

    return mock_jobs


tools = [
    {
        "type": "function",
        "function": {
            "name": "search_jobs",
            "description": "Ищет вакансии по ключевым словам",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Поисковый запрос"},
                    "location": {"type": "string"},
                },
                "required": ["query"],
            },
        },
    }
]


async def main():
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Найди вакансии Python разработчика"}],
        tools=tools,
        tool_choice="auto",  # GPT сам решает когда вызывать
    )

    # Handle tool calls
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            if tool_call.function.name == "search_jobs":
                args = json.loads(tool_call.function.arguments)
                result = search_jobs(**args)
                print("Search results:", result)
    else:
        print("No tool calls made. Response:", response.choices[0].message.content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
