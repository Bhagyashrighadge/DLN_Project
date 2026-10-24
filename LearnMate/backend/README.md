# Smart Document Assistant - Backend

## Overview

This is the backend service for the Smart Document Assistant, a FastAPI-based application that provides document processing, retrieval-augmented generation (RAG), and intelligent chat capabilities.

## Features

- **Document Processing**: PDF extraction and processing
- **Retrieval-Augmented Generation (RAG)**: Intelligent document search and context retrieval
- **Multi-Model Support**: Integration with multiple LLM providers (Google Gemini, DeepSeek)
- **Embeddings**: Sentence transformer-based embeddings for semantic search
- **Vector Store**: ChromaDB for storing and retrieving document embeddings
- **Language Detection**: Multi-language support detection
- **Translation Services**: Cross-language translation capabilities
- **Session Management**: User session tracking and management
- **Audio Logging**: Integration with audio processing modules

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── run_server.py        # Server runner script
├── requirements.txt     # Python dependencies
├── .env                 # Environment configuration
├── api/                 # API routes and endpoints
│   ├── routes.py        # API route definitions
│   ├── schemas.py       # Pydantic models for request/response
│   └── utils.py         # API utility functions
├── services/            # Business logic and external integrations
│   ├── ai_service.py    # AI/LLM service wrapper
│   ├── deepseek_service.py      # DeepSeek LLM integration
│   ├── gemini_service.py        # Google Gemini integration
│   ├── embedding_service.py     # Embedding generation
│   ├── pdf_processor.py         # PDF processing
│   ├── rag_pipeline.py          # RAG pipeline implementation
│   ├── language_detector.py     # Language detection
│   ├── translator.py            # Translation service
│   └── mock_responses.py        # Mock responses for testing
├── models/              # Data models
│   └── session_store.py # Session storage
└── logs/                # Application logs
    └── audio/           # Audio log files
```

## Installation

### Prerequisites

- Python 3.8+
- pip or conda

### Setup

1. **Clone the repository**
   ```bash
   cd LearnMate/backend
   ```

2. **Create a virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env` file or create one with necessary API keys:
     ```
     GOOGLE_API_KEY=your_google_api_key
     DEEPSEEK_API_KEY=your_deepseek_api_key
     DATABASE_URL=your_database_url
     ```

## Running the Server

### Quick Start

```bash
python run_server.py
```

### Manual Startup

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Dependencies

Key dependencies include:

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **langchain**: LLM orchestration
- **python-dotenv**: Environment configuration
- **pdfplumber**: PDF extraction
- **chromadb**: Vector database
- **sentence-transformers**: Embedding generation
- **google-genai**: Google Gemini API
- **requests**: HTTP client

For complete list, see `requirements.txt`

## API Endpoints

The API provides endpoints for:

- Chat and conversation management
- Document upload and processing
- Embeddings generation
- RAG search and retrieval
- Session management
- Language detection and translation

See [API routes](./api/routes.py) for detailed endpoint documentation.

## Configuration

Configuration is managed through:

1. **Environment Variables** (`.env` file)
2. **Settings Module** (if available)
3. **Runtime Configuration** (command-line arguments)

## Testing

Run tests with:

```bash
pytest tests/
```

## Logging

Application logs are stored in the `logs/` directory. Audio logs are saved in `logs/audio/`.

## Contributing

When adding new features:

1. Follow the existing project structure
2. Add appropriate error handling
3. Update documentation
4. Test thoroughly before committing

## License

[Add your license here]

## Support

For issues and questions, please contact [support contact or repository link]
