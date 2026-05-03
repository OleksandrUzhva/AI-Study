import httpx

job_text = """
Для текста вакансии
"""

response = httpx.post(
    "http://127.0.0.1:8000/analyze-job",
    json={
        "job_description": job_text,
        "your_skills": [
            "Python",
            "Django",
            "FastAPI",
            "PostgreSQL",
            "Docker",
            "REST API",
        ],
    },
)
print(response.json())
