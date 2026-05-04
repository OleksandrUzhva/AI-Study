# Job Analyzer AI

An intelligent job analysis and search platform built with FastAPI and OpenAI GPT-4. The application helps job seekers analyze job postings, search for relevant positions, and get AI-powered insights about career opportunities.

## Features

- **Job Analysis**: Analyze job descriptions to extract required skills, tech stack, seniority level, and red flags
- **AI-Powered Job Search**: Intelligent job search with location filtering
- **Conversational Interface**: Chat about jobs in natural language - the AI automatically chooses the right tools
- **Job Comparison**: Compare multiple job opportunities based on custom criteria
- **Structured Output**: Consistent, parseable responses using OpenAI's structured output

## Tech Stack

- **Backend**: FastAPI (Python)
- **AI**: OpenAI GPT-4o-mini with function calling
- **Data Models**: Pydantic
- **Environment**: Python virtual environment

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn openai python-dotenv
   ```

5. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Running the Application

1. **Start the server**:
   ```bash
   uvicorn job_analyzer.main:app --reload
   ```

2. **Access the API**:
   - Interactive docs: http://127.0.0.1:8000/docs
   - Alternative docs: http://127.0.0.1:8000/redoc

## API Endpoints

### 1. `/analyze-job` (POST)
Analyze a single job posting and get structured insights.

**Request Body**:
```json
{
  "job_description": "Python developer with 3+ years experience...",
  "your_skills": ["Python", "Django", "FastAPI", "PostgreSQL"]
}
```

**Response**:
```json
{
  "job_title": "Python Developer",
  "required_skills": ["Python", "Django", "PostgreSQL"],
  "seniority_level": "middle",
  "main_tech_stack": ["Python", "Django", "PostgreSQL"],
  "red_flags": [],
  "match_score": 85
}
```

### 2. `/search-jobs` (POST)
Search for jobs using AI-powered tool calling.

**Request Body**:
```json
{
  "query": "Python developer",
  "location": "Spain"
}
```

**Response**:
```json
{
  "jobs": [
    {
      "title": "Python Developer - Python developer",
      "company": "Tech Corp",
      "location": "Spain",
      "salary": "1000-1500 USD",
      "description": "Looking for Python developer..."
    }
  ],
  "ai_decision": "Used search tool"
}
```

### 3. `/chat-about-job` (POST)
Conversational interface for job-related queries. The AI automatically chooses between analysis, search, or comparison tools.

**Request Body**:
```json
{
  "message": "Проанализируй эту вакансию: Python разработчик с опытом FastAPI"
}
```

**Response** (analysis example):
```json
{
  "analysis": {
    "job_title": "Python Developer",
    "required_skills": ["Python", "FastAPI"],
    "seniority_level": "middle",
    "main_tech_stack": ["Python", "FastAPI"],
    "red_flags": [],
    "match_score": 90
  },
  "ai_decision": "Used analyze_job tool"
}
```

## Usage Examples

### Using curl

**Analyze a job**:
```bash
curl -X POST "http://127.0.0.1:8000/analyze-job" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Junior Python Developer with Django experience",
    "your_skills": ["Python", "Django", "React"]
  }'
```

**Chat about jobs**:
```bash
curl -X POST "http://127.0.0.1:8000/chat-about-job" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Сравни эти вакансии: 1. Python dev 1000 USD, 2. Java dev 1200 USD по зарплате и технологиям"
  }'
```

### Using Python

```python
import requests

# Analyze job
response = requests.post(
    "http://127.0.0.1:8000/analyze-job",
    json={
        "job_description": "Python developer needed",
        "your_skills": ["Python", "Django"]
    }
)
print(response.json())

# Chat interface
response = requests.post(
    "http://127.0.0.1:8000/chat-about-job",
    json={"message": "Проанализируй вакансию Python разработчика"}
)
print(response.json())
```

## AI Features

### Function Calling
The application uses OpenAI's function calling to intelligently route user queries:

- **analyze_job**: For detailed job analysis
- **search_jobs**: For job search queries
- **compare_jobs**: For comparing multiple positions

### Smart Routing
The `/chat-about-job` endpoint automatically determines which tool to use based on the user's natural language input.

## Project Structure

```
job_analyzer/
├── main.py              # Main FastAPI application
├── test_analyze.py      # Test script
└── __pycache__/         # Python cache

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