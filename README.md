# AI Interview Screener

A multi-agent AI backend service for evaluating and ranking candidate interview answers using Groq LLM and LangGraph.

# Live : https://interview-screener-8p59.onrender.com/

## Features

- Multi-agent evaluation system with specialized agents for scoring, analysis, and feedback
- Parallel candidate ranking with batch processing
- Redis-based caching for performance optimization
- FastAPI with async support
- Docker and Render deployment ready

## Quick Start

### Prerequisites

- Python 3.11+
- Redis (for caching, optional)
- Groq API key ([Get one here](https://console.groq.com))

### Local Development

1. Clone the repository:
```bash
git clone <your-repo-url>
cd InterviewScreener
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

5. Start Redis (optional):
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

6. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Evaluate Answer
```bash
POST /evaluate-answer
Content-Type: application/json

{
  "candidate_answer": "I would use a hash map for O(1) lookups...",
  "question_context": "How would you find two numbers that sum to target?"
}
```

Response:
```json
{
  "score": 4,
  "summary": "Solid understanding of hash maps with correct time complexity",
  "improvement": "Consider mentioning space complexity and edge cases"
}
```

### Rank Candidates
```bash
POST /rank-candidates
Content-Type: application/json

{
  "candidates": [
    {
      "candidate_id": "candidate_001",
      "answer": "I would use a hash map..."
    },
    {
      "candidate_id": "candidate_002",
      "answer": "A nested loop would work..."
    }
  ],
  "question_context": "Find two numbers that sum to target"
}
```

### Health Check
```bash
GET /health
```

### API Documentation
Interactive API docs available at `/docs` (Swagger UI)

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GROQ_API_KEY` | Groq API key | Yes | - |
| `REDIS_URL` | Redis connection URL | No | `redis://localhost:6379` |
| `ENVIRONMENT` | Environment (development/production) | No | `development` |
| `LOG_LEVEL` | Logging level | No | `INFO` |
| `ENABLE_CACHING` | Enable Redis caching | No | `true` |
| `LLM_MODEL` | Groq model to use | No | `llama-3.3-70b-versatile` |

## Docker Deployment

```bash
# Build and run
docker compose up --build

# Run in background
docker compose up -d
```

## Render Deployment

1. Push code to GitHub
2. In Render Dashboard, create a new Blueprint
3. Connect your repository (Render will detect `render.yaml`)
4. Set `GROQ_API_KEY` in environment variables
5. Deploy

The `render.yaml` file configures both the web service and Redis database automatically.

## Architecture

The system uses a multi-agent architecture with LangGraph:

1. **Evaluator Agent**: Scores answers on a 1-5 scale
2. **Analyzer Agent**: Identifies strengths, weaknesses, and generates summaries
3. **Improvement Agent**: Provides actionable feedback
4. **Synthesizer**: Combines all outputs into final response

Agents execute sequentially, with results cached in Redis for identical inputs.

## Technology Stack

- **Framework**: FastAPI
- **LLM**: Groq (Llama 3.3 70B)
- **Orchestration**: LangGraph
- **Cache**: Redis
- **Validation**: Pydantic
- **Logging**: Loguru

## Project Structure

```
InterviewScreener/
├── app/
│   ├── agents/          # AI agents (evaluator, analyzer, improvement)
│   ├── api/             # FastAPI routes and dependencies
│   ├── core/            # Configuration, LLM, graph
│   ├── schemas/         # Pydantic models
│   └── services/        # Business logic
├── main.py              # Application entry point
├── requirements.txt     # Dependencies
└── render.yaml         # Render deployment config
```

## License

MIT
