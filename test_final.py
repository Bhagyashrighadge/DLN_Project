#!/usr/bin/env python3
"""
Final comprehensive test for Smart Document Assistant
"""

import requests
import json
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000/api"
TIMEOUT = 60

def test_health():
    """Test health endpoint"""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    try:
        print("Requesting: GET /api/health")
        response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT)
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"  Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_upload():
    """Test PDF upload"""
    print("\n" + "="*80)
    print("TEST 2: Upload PDF")
    print("="*80)
    
    try:
        pdf_path = Path("test_document.pdf")
        
        if not pdf_path.exists():
            print(f"✗ PDF not found: {pdf_path}")
            return False, None
        
        print(f"Uploading: {pdf_path} ({pdf_path.stat().st_size} bytes)")
        
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path.name, f, 'application/pdf')}
            response = requests.post(
                f"{API_BASE_URL}/upload-pdf",
                files=files,
                timeout=TIMEOUT
            )
        
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"  Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get('success'):
            session_id = data.get('session_id')
            print(f"✓ PDF uploaded! Session ID: {session_id}")
            return True, session_id
        return False, None
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def test_ask_question(session_id, question, language="en"):
    """Test asking a question"""
    print(f"\n  Question: \"{question}\"")
    print(f"  Language: {language}")
    print("  " + "-" * 60)
    
    try:
        payload = {
            "session_id": session_id,
            "question": question,
            "language": language
        }
        
        response = requests.post(
            f"{API_BASE_URL}/ask-question",
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code != 200:
            data = response.json()
            print(f"  ✗ Status: {response.status_code}")
            print(f"    Error: {data.get('detail', response.text)}")
            return False
        
        data = response.json()
        
        if data.get('success'):
            answer = data['answer']
            # Show first 150 chars
            preview = answer[:150] + "..." if len(answer) > 150 else answer
            print(f"  ✓ Answer received ({len(answer)} chars)")
            print(f"    Preview: {preview}")
            return True
        else:
            print(f"  ✗ Error: {data.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"  ✗ Exception: {str(e)}")
        return False

def main():
    print("\n" + "="*80)
    print("SMART DOCUMENT ASSISTANT - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Backend URL: {API_BASE_URL}")
    print(f"Timeout: {TIMEOUT} seconds")
    
    # Test 1: Health Check
    if not test_health():
        print("\n❌ Backend health check failed - cannot proceed")
        return
    
    print("\n✓ Backend is healthy!\n")
    
    # Test 2: Upload PDF
    success, session_id = test_upload()
    if not success or not session_id:
        print("\n❌ PDF upload failed - cannot proceed with questions")
        return
    
    # Test 3: Ask Questions in Multiple Languages
    print("\n" + "="*80)
    print("TEST 3: Ask Questions (English, Hindi, Marathi)")
    print("="*80)
    
    test_cases = [
        ("What is Python?", "en"),
        ("Python क्या है?", "hi"),
        ("Python म्हणजे काय?", "mr"),
    ]
    
    results = []
    for idx, (question, language) in enumerate(test_cases, 1):
        print(f"\n  Test 3.{idx}: {language.upper()}")
        time.sleep(0.5)  # Small delay between requests
        result = test_ask_question(session_id, question, language)
        results.append((question, language, result))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for idx, (question, language, result) in enumerate(results, 1):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} | Test 3.{idx} ({language.upper()}) | {question[:40]}")
    
    passed = sum(1 for _, _, r in results if r)
    total = len(results)
    
    print(f"\n  Questions Answered: {passed}/{total}")
    
    # Final status
    print("\n" + "="*80)
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is fully functional.")
        print("\nThe Smart Document Assistant is ready for use:")
        print("  ✓ Backend Health: OK")
        print("  ✓ PDF Upload: OK")
        print(f"  ✓ Questions: OK ({total}/{total})")
        print(f"  ✓ Languages: English, Hindi, Marathi")
    else:
        print(f"⚠️  {total - passed} test(s) failed.")
        print("\nPassing tests:")
        print("  ✓ Backend Health: OK")
        print("  ✓ PDF Upload: OK")
        print(f"  ✓ Questions: {passed}/{total} passed")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
