import httpx

job_text = """
About the job
About The Role

At Blazity, we are building modern web applications and rapidly expanding into AI-powered systems — agents, automation, and LLM-based workflows.

We are looking for a high-potential Junior AI Developer (student or early career) who is strongly interested in AI and LLMs, actively experiments with them, and wants to turn that into real-world, production experience.

This is not a standard frontend role — this is an AI-first position, where web development is a tool to build intelligent systems.

Our Requirements

AI-first mindset

You actively use agentic coding tools like: Claude Code / Codex / Cursor
You have experimented with AI, e.g.:
building a chatbot
automating tasks with LLMs
generating structured outputs
You are curious:
how LLMs work
how to build real AI features (not just use them)
This role is for people who already do things with AI, not just read about it.
 Technical foundations

Knowledge of:
JavaScript / TypeScript
React or Next.js (even small projects)
Understanding of APIs (REST basics)
 Learning mindset

You learn by building (projects > theory)
You are comfortable making mistakes and iterating
You are proactive and self-driven

Big plus

First experience with:
OpenAI / Anthropic APIs
prompt engineering (structured output, few-shot)
You built:
small AI apps (chatbot, automation, AI tool)
GitHub projects showing AI experiments
Participation in hackathons (especially AI-related)
 Other

English C1

What You Will Do

Work on real AI features
Support development of:
LLM-based features
simple AI workflows
early-stage agent-like systems
Help with:
prompt design and iteration
testing and improving AI outputs
building simple integrations with LLM APIs
What We Offer

Hands-on experience with real AI systems in production
Work with experienced engineers building AI solutions
Fast growth path toward AI Engineer role
Opportunity to work on real client projects (not toy problems)

Location

100% remote from Poland
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
    timeout=120.0,
)
print(response.json())
