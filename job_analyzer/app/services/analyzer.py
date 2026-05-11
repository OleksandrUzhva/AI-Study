import openai
from openai import AsyncOpenAI
from fastapi import HTTPException
from typing import List
from app.models.schemas import JobAnalysis, AnalyzeRequest
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)


async def analyze_job_function(request: AnalyzeRequest) -> JobAnalysis:
    prompt = f"""<job_description>
{request.job_description}
</job_description>

<candidate_skills>
{', '.join(request.your_skills)}
</candidate_skills>"""

    try:
        response = await client.beta.chat.completions.parse(
            model=settings.model,
            messages=[
                {
                    "role": "system",
                    "content": """Ты опытный технический рекрутер с 10 годами опыта.

    При анализе вакансии рассуждай по шагам:
    1. Выдели обязательные технические требования из <job_description>
    2. Сравни каждое требование с навыками из <candidate_skills>
    3. Найди красные флаги: нереалистичные требования для уровня,
    отсутствие зарплаты, признаки переработок, расплывчатые обязанности
    4. Рассчитай match_score только по техническим навыкам (0-100)
    5. Дай конкретную рекомендацию

    Примеры красных флагов высокой серьёзности:
    - "Senior опыт за Junior зарплату"
    - "Работа в выходные по необходимости"
    - Требуется 5+ технологий для Junior позиции""",
                },
                {"role": "user", "content": prompt},
            ],
            response_format=JobAnalysis,
        )
        return response.choices[0].message.parsed
    except openai.RateLimitError:
        raise HTTPException(
            status_code=429, detail="Слишком много запросов. Пожалуйста, подождите."
        )
    except openai.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка OpenAI: {str(e)}")


async def compare_jobs_function(jobs: List[str], criteria: List[str]) -> str:
    prompt = f"""Сравни следующие вакансии по заданным критериям.

Вакансии:
{chr(10).join(f"{i+1}. {job}" for i, job in enumerate(jobs))}

Критерии для сравнения:
{chr(10).join(f"- {criterion}" for criterion in criteria)}

Дай подробное сравнение, укажи преимущества и недостатки каждой вакансии."""

    response = await client.chat.completions.create(
        model=settings.model, messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def search_jobs(query: str, location: str = None) -> list:
    """Мок — в реальном проекте здесь был бы вызов LinkedIn API"""
    mock_jobs = [
        {
            "title": f"Python Developer - {query}",
            "company": "Tech Corp",
            "location": location or "Remote",
            "salary": "1000-1500 USD",
        },
        {
            "title": f"Junior Python Engineer - {query}",
            "company": "Innovate Ltd",
            "location": location or "Spain",
            "salary": "1000-1500 USD",
        },
    ]
    if location:
        mock_jobs = [j for j in mock_jobs if location.lower() in j["location"].lower()]
    return mock_jobs
