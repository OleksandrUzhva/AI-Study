from fastapi import FastAPI 
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel 
from openai import AsyncOpenAI 
from dotenv import load_dotenv 
from typing import List

import openai
import os


load_dotenv() 
app = FastAPI() 
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")) 

class ChatRequest(BaseModel): 
    message: str 
    system: str = "Ты помощник разработчика" 

class ChatResponse(BaseModel): 
    reply: str 
    tokens_used: int 

@app.post("/chat", response_model=ChatResponse) 
async def chat(request: ChatRequest): 
    try:
        response = await client.chat.completions.create( 
            model="gpt-4o-mini", 
            messages=[ 
                {"role": "system", "content": request.system}, 
                {"role": "user", "content": request.message} 
            ] 
        ) 
        return ChatResponse( 
            reply=response.choices[0].message.content, 
            tokens_used=response.usage.total_tokens 
        )
    except openai.RateLimitError: 
        raise HTTPException(429, "Слишком много запросов, подожди немного")
    except openai.APITimeoutError: 
        raise HTTPException(504, "OpenAI не ответил вовремя")
    except openai.APIError as e: 
        raise HTTPException(503, f"Ошибка API: {str(e)}")


async def generate_stream(message: str): 
    try:
        stream = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message}],
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield f"data: {delta}\n\n"
        yield "data: [DONE]\n\n"

    except openai.RateLimitError:
        yield "data: [ERROR] Слишком много запросов, подожди немного\n\n"
    except openai.APITimeoutError:
        yield "data: [ERROR] OpenAI не ответил вовремя\n\n"
    except openai.APIError as e:
        yield f"data: [ERROR] Ошибка API: {str(e)}\n\n"

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest): 
    return StreamingResponse( generate_stream(request.message), 
    media_type="text/event-stream" )


class JobAnalysis(BaseModel): 
    job_title: str 
    required_skills: List[str] 
    seniority_level: str # junior / middle / senior 
    main_tech_stack: List[str] 
    red_flags: List[str] 
    match_score: int # 0-100 

# Structured output — схема гарантирована 
response = client.beta.chat.completions.parse( 
    model="gpt-4o-mini", 
    messages=[ 
        {"role": "system", "content": "Анализируй вакансии и возвращай структурированные данные"}, 
        {"role": "user", "content": "Вакансия: Python Backend Developer, нужен Django, PostgreSQL, 2+ года опыта..."} 
    ], 
    response_format=JobAnalysis 
) 
analysis: JobAnalysis = response.choices[0].message.parsed 
print(analysis.match_score) # сразу int, не строка