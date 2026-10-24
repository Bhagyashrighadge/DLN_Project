"""
Gemini Service - Integration with Google Gemini API for LLM responses
"""
import google.genai as genai
import logging
from typing import Optional
import os

from services.language_detector import (
    get_strict_language_instruction,
    validate_language_strict,
)

logger = logging.getLogger(__name__)


class GeminiService:
    """Handles communication with Google Gemini API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini service

        Args:
            api_key: Google Gemini API key (if not provided, uses env variable)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not provided or set in environment")

        # Configure Gemini client
        self.client = genai.Client(api_key=self.api_key)

        # Retry configuration
        self.max_language_validation_retries = 3

        logger.info("[GEMINI] Service initialized successfully")

    def generate_response(
        self,
        prompt: str,
        context: str = "",
        language: str = "en",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        retry_attempt: int = 1,
    ) -> Optional[str]:
        """
        Generate response from Gemini API with strict language enforcement

        Args:
            prompt: User question
            context: Document context
            language: Target language (en, hi, mr)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            retry_attempt: Retry counter for language enforcement

        Returns:
            Response text or None
        """
        try:
            if not prompt or not prompt.strip():
                logger.error("[GEMINI] Empty prompt")
                return None

            # 🔒 Strict language instruction
            language_instruction = get_strict_language_instruction(language)

            system_message = f"""
You are a helpful assistant answering questions based ONLY on the provided document context.

{language_instruction}

Rules:
- Answer ONLY in {language}
- Do NOT mix languages
- Do NOT mention document chunks or references
- If the answer is not found in the context, clearly say so
"""

            if context and context.strip():
                full_prompt = f"""{system_message}

Context from the document:
{context}

Question:
{prompt}
"""
            else:
                full_prompt = f"""{system_message}

Question:
{prompt}
"""

            logger.info(f"[GEMINI] Attempt {retry_attempt}")
            logger.info(f"[GEMINI] Language: {language}")
            logger.info(f"[GEMINI] Prompt length: {len(full_prompt)} chars")

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    top_p=0.9,
                ),
            )

            # Extract text safely
            answer = None

            if hasattr(response, "text") and response.text:
                answer = response.text.strip()
            elif response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    part = candidate.content.parts[0]
                    if hasattr(part, "text"):
                        answer = part.text.strip()

            if not answer:
                logger.error("[GEMINI] No text found in response")
                return None

            logger.info(f"[GEMINI] Answer received ({len(answer)} chars)")

            # ✅ Language validation
            is_valid = validate_language_strict(
                answer, language, min_confidence=0.55
            )

            if is_valid:
                logger.info("[GEMINI] ✓ Language validation passed")
                return answer

            logger.warning("[GEMINI] ✗ Language validation failed")

            # Retry if language mismatch
            if retry_attempt < self.max_language_validation_retries:
                logger.info(
                    f"[GEMINI] Retrying with stricter prompt "
                    f"({retry_attempt + 1}/{self.max_language_validation_retries})"
                )
                return self.generate_response(
                    prompt=prompt,
                    context=context,
                    language=language,
                    temperature=min(temperature + 0.2, 1.3),
                    max_tokens=max_tokens,
                    retry_attempt=retry_attempt + 1,
                )

            # Last attempt – return anyway
            logger.warning("[GEMINI] Returning response after max retries")
            return answer

        except Exception as e:
            logger.error(f"[GEMINI] Request failed: {type(e).__name__}: {str(e)}")
            logger.exception("Full traceback:")
            return None

    def test_connection(self) -> bool:
        """
        Test connection to Gemini API
        """
        try:
            logger.info("[GEMINI] Testing API connection...")
            response = self.generate_response(
                prompt="Hello",
                language="en",
                max_tokens=50
            )
            if response:
                logger.info("[GEMINI] ✓ Connection successful")
                return True
            logger.error("[GEMINI] ✗ Connection failed")
            return False
        except Exception as e:
            logger.error(f"[GEMINI] Connection test failed: {str(e)}")
            return False
