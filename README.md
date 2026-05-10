# Job Analyzer AI

FastAPI app in `job_analyzer/` for job description analysis, AI job search, and chat-based job assistance.

## Quick start

1. `cd job_analyzer`
2. create `.env` with `OPENAI_API_KEY=...`
3. `python -m venv venv`
4. activate the environment
5. `pip install -r requirements.txt`
6. `uvicorn main:app --reload`

Open docs at `http://127.0.0.1:8000/docs`.

## Endpoints

- `POST /analyze-job` — analyze a job description
- `POST /search-jobs` — search jobs with AI support
- `POST /chat-about-job` — conversational job queries with tool routing

## Deploy

- Railway root should be `job_analyzer` if supported.
- Otherwise use the repository root `Dockerfile`.

## Notes

- Uses `fastapi`, `uvicorn`, `python-dotenv`, and `openai`
- Main app file: `job_analyzer/main.py`
- Requirements: `job_analyzer/requirements.txt`


- Use the root-level `Dockerfile` in the repository root.
- Railway will build the app from the `job_analyzer/` folder by copying `job_analyzer/requirements.txt` and application files.
- If Railway allows specifying a service root, set it to `job_analyzer`.

### Build locally with Docker

From the repository root:

```bash
docker build -t job-analyzer .
``` 

Run the container:

```bash
docker run -p 8000:8000 job-analyzer
```

The API will be available at `http://127.0.0.1:8000`.

## Project Structure

```
job-analyzer/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── jobs.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analyzer.py
│   │   └── session.py
│   └── models/
│       ├── __init__.py
│       └── schemas.py
└── requirements.txt

ai_backend_learning/     # Additional learning materials
.gitignore              # Git ignore rules
.env                   # Environment variables (not committed)
venv/                  # Virtual environment
```

## Development

### Running Tests
```bash
python job_analyzer/test_analyze.py
```

### Standalone AI Testing
```bash
python job_analyzer/main.py
```

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for API calls

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Please ensure compliance with OpenAI's terms of service when using their API.

## Future Enhancements

- Integration with real job search APIs (LinkedIn)
- User authentication and profiles
- Job application tracking
- Resume optimization suggestions
- Multi-language support