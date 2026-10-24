"""
API Routes - Define all API endpoints (Gemini LLM)
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
import logging
import sys
from pathlib import Path

# Add parent directory to path for absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.schemas import (
    UploadResponse,
    QuestionRequest,
    QuestionResponse,
    TranslateRequest,
    TranslateResponse,
    HealthResponse,
    SessionInfoResponse,
    ChatMessage,
)
from api.utils import save_upload_file, cleanup_temp_file, validate_pdf_file
from services.pdf_processor import PDFProcessor
from services.rag_pipeline import RAGPipeline
from services.gemini_service import GeminiService
from services.translator import TranslatorService
from models.session_store import session_store

router = APIRouter()
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Global instances
# ------------------------------------------------------------------

pdf_processor = PDFProcessor()
translator_service = TranslatorService()
gemini_service: Optional[GeminiService] = None

# Session-specific RAG pipelines
rag_pipelines = {}

# ------------------------------------------------------------------
# Gemini service factory
# ------------------------------------------------------------------

def get_gemini_service() -> GeminiService:
    global gemini_service
    if gemini_service is None:
        try:
            gemini_service = GeminiService()
            logger.info("[GEMINI] Service initialized successfully")
        except Exception as e:
            logger.error(f"[GEMINI] Initialization failed: {str(e)}")
            raise
    return gemini_service

# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------

@router.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        get_gemini_service()
        return HealthResponse(
            status="healthy",
            message="All services operational (Gemini API ready)"
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            message=f"Gemini API error: {str(e)}"
        )

# ------------------------------------------------------------------
# Upload PDF
# ------------------------------------------------------------------

@router.post("/upload-pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):

    if not validate_pdf_file(file):
        raise HTTPException(
            status_code=400,
            detail="Invalid file. Please upload a PDF file."
        )

    session_id = session_store.create_session()
    temp_file_path = None

    try:
        temp_file_path = await save_upload_file(file)
        if not temp_file_path:
            raise HTTPException(status_code=500, detail="Failed to save file")

        text = pdf_processor.extract_text(temp_file_path)
        if not text:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract text from PDF"
            )

        text = pdf_processor.clean_text(text)
        chunks = pdf_processor.chunk_text(text)

        rag_pipeline = RAGPipeline()
        rag_pipeline.create_collection(f"session_{session_id}")
        rag_pipeline.add_documents(chunks)

        rag_pipelines[session_id] = rag_pipeline

        session_store.update_session(
            session_id,
            document_name=file.filename,
            document_text=text
        )

        return UploadResponse(
            success=True,
            session_id=session_id,
            message=f"Successfully processed '{file.filename}'",
            document_name=file.filename
        )

    except Exception as e:
        session_store.delete_session(session_id)
        rag_pipelines.pop(session_id, None)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )

    finally:
        if temp_file_path:
            cleanup_temp_file(temp_file_path)

# ------------------------------------------------------------------
# Ask Question (Gemini + RAG)
# ------------------------------------------------------------------

@router.post("/ask-question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):

    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired"
        )

    if request.language not in ["en", "hi", "mr"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid language. Supported: en, hi, mr"
        )

    rag_pipeline = rag_pipelines.get(request.session_id)
    if not rag_pipeline:
        raise HTTPException(
            status_code=500,
            detail="RAG pipeline not initialized"
        )

    logger.info("=" * 60)
    logger.info("[ASK QUESTION]")
    logger.info(f"Question: {request.question}")
    logger.info(f"Language: {request.language}")

    # Retrieve context
    context = rag_pipeline.get_context(request.question, top_k=3)
    if not context.strip():
        return QuestionResponse(
            success=False,
            answer="",
            original_answer="",
            language=request.language,
            message="No relevant information found in the document."
        )

    # Gemini response
    try:
        service = get_gemini_service()
        original_answer = service.generate_response(
            prompt=request.question,
            context=context,
            language=request.language
        )

        if not original_answer:
            raise HTTPException(
                status_code=500,
                detail="Gemini failed to generate a response"
            )

    except Exception as e:
        logger.error(f"[GEMINI ERROR] {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Gemini error: {str(e)}"
        )

    # Store chat history
    session_store.add_message(request.session_id, "user", request.question)
    session_store.add_message(request.session_id, "assistant", original_answer)
    session_store.update_session(request.session_id, language=request.language)

    logger.info("[SUCCESS] Answer generated")
    logger.info("=" * 60)

    return QuestionResponse(
        success=True,
        answer=original_answer,
        original_answer=original_answer,
        language=request.language
    )

# ------------------------------------------------------------------
# Translate
# ------------------------------------------------------------------

@router.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):

    if request.target_language not in ["en", "hi", "mr"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid language. Supported: en, hi, mr"
        )

    translated = translator_service.translate(
        request.text,
        request.target_language
    )

    return TranslateResponse(
        success=True,
        original_text=request.text,
        translated_text=translated,
        target_language=request.target_language
    )

# ------------------------------------------------------------------
# Session Info
# ------------------------------------------------------------------

@router.get("/session/{session_id}", response_model=SessionInfoResponse)
async def get_session_info(session_id: str):

    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    chat_messages = [
        ChatMessage(
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp.isoformat()
        )
        for msg in session.chat_history
    ]

    return SessionInfoResponse(
        session_id=session.session_id,
        document_name=session.document_name,
        created_at=session.created_at.isoformat(),
        language=session.language,
        chat_history=chat_messages
    )

# ------------------------------------------------------------------
# Delete Session
# ------------------------------------------------------------------

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):

    success = session_store.delete_session(session_id)
    rag_pipelines.pop(session_id, None)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return {"success": True, "message": "Session deleted"}
