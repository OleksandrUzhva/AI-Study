from uuid import uuid4
from app.config import settings

sessions: dict[str, list[dict[str, str]]] = {}


def get_or_create_session(session_id: str | None, your_skills: list[str]) -> str:
    sid = session_id or str(uuid4())
    if sid not in sessions:
        skills_str = ", ".join(your_skills)
        sessions[sid] = [
            {
                "role": "system",
                "content": f"""Ты помощник по анализу вакансий.
Навыки кандидата: {skills_str}.
Не спрашивай навыки повторно — они уже известны.""",
            }
        ]
    return sid


def add_message(sid: str, role: str, content: str) -> None:
    sessions[sid].append({"role": role, "content": content})
    if len(sessions[sid]) > settings.max_history:
        sessions[sid] = [sessions[sid][0]] + sessions[sid][-settings.max_history + 1 :]


def get_history(sid: str) -> list:
    return sessions.get(sid, [])
