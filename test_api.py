#!/usr/bin/env python3
"""
Test script for the Smart Document Assistant API
Tests the ask-question endpoint with comprehensive debugging
"""

import requests
import json
import time
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

# Configuration
API_BASE_URL = "http://localhost:8000/api"
TIMEOUT = 60

def create_test_pdf():
    """Create a simple test PDF"""
    print("[TEST] Creating test PDF...")
    
    # Create a simple PDF with some sample text
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Add some test content
    c.setFont("Helvetica", 12)
    y = 750
    
    test_text = [
        "This is a test document for the Smart Document Assistant.",
        "",
        "Python is a high-level, interpreted programming language.",
        "It supports multiple programming paradigms including:",
        "- Imperative programming",
        "- Functional programming", 
        "- Object-oriented programming",
        "",
        "The language emphasizes code readability with significant whitespace.",
        "",
        "In Hindi: Python एक महत्वपूर्ण प्रोग्रामिंग भाषा है।",
        "In Marathi: Python एक शक्तिशाली प्रोग्रामिंग भाषा आहे।",
        "",
        "Python was created by Guido van Rossum and first appeared in 1991.",
        "It is now maintained by the Python Software Foundation.",
    ]
    
    for line in test_text:
        c.drawString(50, y, line)
        y -= 20
    
    c.save()
    buffer.seek(0)
    return buffer

def test_health_check():
    """Test the health check endpoint"""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def test_upload_pdf():
    """Test PDF upload"""
    print("\n" + "="*80)
    print("TEST 2: Upload PDF")
    print("="*80)
    
    try:
        # Create test PDF
        pdf_buffer = create_test_pdf()
        
        # Upload
        files = {'file': ('test_document.pdf', pdf_buffer, 'application/pdf')}
        response = requests.post(
            f"{API_BASE_URL}/upload-pdf",
            files=files,
            timeout=TIMEOUT
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get('success'):
            return True, data.get('session_id')
        return False, None
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False, None

def test_ask_question(session_id, question, language="en"):
    """Test asking a question"""
    print(f"\n[QUESTION] Testing: {question} (Language: {language})")
    print("-" * 60)
    
    try:
        payload = {
            "session_id": session_id,
            "question": question,
            "language": language
        }
        
        print(f"Request: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{API_BASE_URL}/ask-question",
            json=payload,
            timeout=TIMEOUT
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error Response: {response.text}")
            return False
        
        data = response.json()
        
        if data.get('success'):
            print(f"✓ Answer (first 200 chars): {data['answer'][:200]}...")
            return True
        else:
            print(f"✗ Failed: {data.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("SMART DOCUMENT ASSISTANT - API TEST SUITE")
    print("="*80)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Health check failed - backend may not be running")
        return
    
    print("\n✓ Health check passed")
    
    # Test 2: Upload PDF
    success, session_id = test_upload_pdf()
    if not success:
        print("\n❌ PDF upload failed")
        return
    
    print(f"\n✓ PDF uploaded successfully (Session: {session_id})")
    
    # Test 3: Ask questions in different languages
    print("\n" + "="*80)
    print("TEST 3: Ask Questions (Multiple Languages)")
    print("="*80)
    
    tests = [
        ("What is Python?", "en"),
        ("Python क्या है?", "hi"),
        ("Python म्हणजे काय?", "mr"),
    ]
    
    results = []
    for question, language in tests:
        time.sleep(1)  # Small delay between requests
        result = test_ask_question(session_id, question, language)
        results.append((question, language, result))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for question, language, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} | {language.upper():5} | {question}")
    
    passed = sum(1 for _, _, r in results if r)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")

if __name__ == "__main__":
    main()
