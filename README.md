# AskDocAI - Smart Document Assistant (RAG Chatbot)
Deep Learning Networks (DLN) Research Challenge & Prototype

## Project Overview
This repository contains the complete implementation of **AskDocAI**, an intelligent, multilingual Retrieval-Augmented Generation (RAG) assistant for querying PDF documents in English, Hindi, and Marathi.

## Core Modules & Directory Layout
- **`LearnMate/`**: The complete production-grade application:
  - `backend/`: FastAPI application with modular RAG, embeddings, language detection, translation, and LLM services.
  - `frontend/`: React + Vite + Tailwind CSS responsive single-page web interface.
- **`rag_pipeline/`**: Standalone vector indexing and retrieval subsystem.
- **`llm_backend/`**: LLM query and orchestration layer.
- **`text_processing/`**: PDF text extraction and normalization pipeline.
- **`Backend API INT/`**: Core API schema definitions and baseline routes.
- **`frontend_rag/`**: Vanilla web client prototype.
- **`test_*.py`**: Comprehensive automated test harness for health checks, PDF upload, embedding generation, retrieval, and Q&A workflows.

## Quick Start

### Backend Setup
```bash
cd LearnMate/backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate
pip install -r requirements.txt
python run_server.py
```

### Frontend Setup
```bash
cd LearnMate/frontend
npm install
npm run dev
```

For detailed architecture diagrams and integration guides, see [`LearnMate/README.md`](LearnMate/README.md).
