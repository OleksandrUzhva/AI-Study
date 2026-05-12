import openai
from typing import List, AsyncGenerator
from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.models.schemas import JobAnalysis, AnalyzeRequest
from app.services.session import get_session_history
from app.config import settings


llm_structured = ChatOpenAI(
    model=settings.model,
    api_key=settings.openai_api_key,
    temperature=0,  
).with_structured_output(JobAnalysis)

llm_chat = ChatOpenAI(
    model="gpt-4o-mini", api_key=settings.openai_api_key, streaming=True
)


SYSTEM_ANALYZE = "Ты технический рекрутер с 10-летним опытом. Проанализируй вакансию и выдели главное."
SYSTEM_CHAT = "Ты технический рекрутер. Помогаешь кандидату разобраться в вакансии, используя историю чата."


async def analyze_job_function(request: AnalyzeRequest) -> JobAnalysis:
    """Анализ вакансии через LangChain с структурированным выводом."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_ANALYZE),
            (
                "human",
                "Проанализируй вакансию: {job_description}\nМои навыки: {your_skills}",
            ),
        ]
    )

    chain = prompt | llm_structured

    try:
        return await chain.ainvoke(
            {
                "job_description": request.job_description,
                "your_skills": ", ".join(request.your_skills),
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")


async def chat_with_job_streaming(
    message: str, session_id: str
) -> AsyncGenerator[str, None]:
    """Потоковый чат с сохранением истории сессии."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_CHAT),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
        ]
    )

    chain = prompt | llm_chat | StrOutputParser()

    with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    config = {"configurable": {"session_id": session_id}}

    try:
        async for chunk in with_history.astream({"input": message}, config=config):
            yield chunk
    except openai.RateLimitError:
        raise HTTPException(status_code=429, detail="Лимит запросов исчерпан.")


async def compare_jobs_function(jobs: List[str], criteria: List[str]) -> str:
    """Сравнение вакансий (тоже переведено на LangChain для единообразия)."""
    prompt = ChatPromptTemplate.from_template(
        "Сравни вакансии: {jobs}\nКритерии: {criteria}"
    )
    chain = prompt | llm_chat | StrOutputParser()

    return await chain.ainvoke(
        {"jobs": "\n".join(jobs), "criteria": ", ".join(criteria)}
    )


def search_jobs(query: str, location: str = None) -> list:
    """Мок поиска вакансий."""
    mock_jobs = [
        {
            "title": f"Python Dev - {query}",
            "company": "Tech",
            "location": location or "Remote",
        },
        {
            "title": f"Junior Dev - {query}",
            "company": "Innovate",
            "location": location or "Spain",
        },
    ]
    if location:
        return [j for j in mock_jobs if location.lower() in j["location"].lower()]
    return mock_jobs
