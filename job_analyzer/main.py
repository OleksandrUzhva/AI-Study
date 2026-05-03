from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from openai import AsyncOpenAI
import os

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


@app.post("/analyze-job", response_model=JobAnalysis)
async def analyze_job(request: AnalyzeRequest):
    prompt = f"""Проанализируй вакансию и оцени соответствие кандидата.
            Навыки кандидата: {', '.join(request.your_skills)}
            Вакансия: {request.job_description}"""
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
