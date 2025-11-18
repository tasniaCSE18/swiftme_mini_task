# Swiftme Mini - Smart Job Proposal Generator

A simplified RAG-powered job proposal generator built with LangChain, FastAPI and OpenAI.

## Features

-  **RAG System**: Vector database (ChromaDB) for semantic search of freelancer experience
- **LangChain Workflow**: Multi-step proposal generation pipeline
- **Smart Extraction**: Automated job requirements analysis
- **Match Scoring**: Confidence scores based on skill matching
- **Proposal History**: Track last 5 generated proposals


## Setup Instructions

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd swiftme-mini
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add  OpenAI API key
```

5. **Run the application**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

### 1. Setup Profile

**Endpoint**: `POST /api/profile/setup`

**Request Body**:
```json
{
  "name": "John Doe",
  "skills": ["React", "Node.js", "Python", "AI/ML"],
  "experience": "5 years full-stack development with focus on AI integration",
  "past_projects": [
    "E-commerce platform with 10k+ users",
    "AI chatbot using OpenAI GPT-3"
  ],
  "rate": "$50-75/hour"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Profile for John Doe stored successfully",
  "documents_stored": 6
}
```

### 2. Generate Proposal

**Endpoint**: `POST /api/proposal/generate`

**Request Body**:
```json
{
  "job_text": "Looking for a developer to build a Chrome extension that uses AI to help with content writing. Requirements: JavaScript, Chrome APIs, OpenAI integration. Budget: $1000-2000"
}
```

**Response**:
```json
{
  "proposal": "Hello,\n\n I saw that you're seeking a Chrome extension developer experienced in AI integration. With five years in full-stack development and direct involvement in creating an AI chatbot, I'm certain I can provide precisely what you're after. My background includes working with Chrome APIs and incorporating OpenAI, which fits your needs.\n\n Regards",
  "confidence_score": 0.85,
  "matched_skills": ["JavaScript", "AI/ML", "OpenAI"]
}
```

### 3. Get Proposal History

**Endpoint**: `GET /api/proposal/history`

**Response**:
```json
{
  "proposals": [
    {
      "job_text": "Looking for a developer...",
      "proposal": "Hi there...",
      "confidence_score": 0.85,
      "matched_skills": ["JavaScript", "AI/ML"]
    }
  ]
}
```

## Testing with cURL

```bash
# 1. Setup profile
curl -X POST http://localhost:8000/api/profile/setup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "skills": ["React", "Node.js", "Python"],
    "experience": "5 years full-stack development",
    "past_projects": ["E-commerce platform", "AI chatbot"]
  }'

# 2. Generate proposal
curl -X POST http://localhost:8000/api/proposal/generate \
  -H "Content-Type: application/json" \
  -d '{
    "job_text": "Need a React developer for e-commerce project"
  }'

# 3. Get history
curl http://localhost:8000/api/proposal/history
```

