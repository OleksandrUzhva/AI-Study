from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from openai import AsyncOpenAI
import os
import json

load_dotenv()
app = FastAPI()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class JobAnalysis(BaseModel):
    job_title: str
    required_skills: List[str]
    seniority_level: str  # junior / middle / senior
    main_tech_stack: List[str]
    red_flags: List[str]
    match_score: int  # 0-100


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


async def analyze_job_function(job_description: str, your_skills: List[str] = None):
    """Helper function for analyzing a job posting."""
    if your_skills is None:
        your_skills = ["Python", "Django", "FastAPI", "PostgreSQL", "Docker", "REST API"]
    
    prompt = f"""Проанализируй вакансию и оцени соответствие кандидата.
            Навыки кандидата: {', '.join(your_skills)}
            Вакансия: {job_description}"""
    
    response = await client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """Ты опытный технический рекрутер. Анализируй вакансии и выявляй:
                - required_skills: только обязательные технические навыки
                - main_tech_stack: основные технологии проекта
                - red_flags: тревожные признаки вакансии — нереалистичные требования, 
                  отсутствие зарплаты, расплывчатые обязанности, признаки переработок.
                  Если красных флагов нет — возвращай пустой список.
                - match_score: 0-100 насколько навыки кандидата совпадают с требованиями"""
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
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
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
    return await analyze_job_function(request.job_description, request.your_skills)


@app.post("/chat-about-job")
async def chat_about_job(request: ChatRequest):
    """
    Endpoint for chatting about jobs in free form.
    The AI will decide whether to call analyze_job or compare_jobs based on the message.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "analyze_job",
                "description": "Анализирует вакансию и оценивает соответствие кандидата",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_description": {"type": "string", "description": "Описание вакансии"},
                        "your_skills": {"type": "array", "items": {"type": "string"}, "description": "Навыки кандидата"}
                    },
                    "required": ["job_description"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "compare_jobs",
                "description": "Сравнивает несколько вакансий по заданным критериям",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "jobs": {"type": "array", "items": {"type": "string"}, "description": "Список описаний вакансий"},
                        "criteria": {"type": "array", "items": {"type": "string"}, "description": "Критерии для сравнения"}
                    },
                    "required": ["jobs", "criteria"]
                }
            }
        }
    ]

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": request.message}],
        tools=tools,
        tool_choice="auto"
    )

    # Handle tool calls
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            if tool_call.function.name == "analyze_job":
                args = json.loads(tool_call.function.arguments)
                result = await analyze_job_function(**args)
                return {"analysis": result, "ai_decision": "Used analyze_job tool"}
            elif tool_call.function.name == "compare_jobs":
                args = json.loads(tool_call.function.arguments)
                result = await compare_jobs_function(**args)
                return {"comparison": result, "ai_decision": "Used compare_jobs tool"}

    # If no tool calls, return AI's direct response
    return {
        "response": response.choices[0].message.content,
        "ai_decision": "Direct response"
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
