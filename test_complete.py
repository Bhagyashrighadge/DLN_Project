#!/usr/bin/env python3
"""
Test script for Smart Document Assistant - using minimal PDF creation
"""

import requests
import json
import time
from pathlib import Path
import os

# Configuration
API_BASE_URL = "http://localhost:8000/api"
TIMEOUT = 60

# Create a minimal PDF file manually (base64 encoded simple PDF)
# This is a minimal valid PDF without any external dependencies
MINIMAL_PDF_B64 = """JVBERi0xLjANCjEgMCBvYmo8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFI+PmVuZG9iag
oyIDAgb2JqPDwvVHlwZS9QYWdlcy9LaWRzWzMgMCBSXS9Db3VudCAxPj5lbmRvYmoKMyAw
IG9iajw8L1R5cGUvUGFnZS9QYXJlbnQgMiAwIFIvUmVzb3VyY2VzPDwvRm9udDw8L0YxIDQg
MCBSPj4+Pj4vTWVkaWFCb3hbMCAwIDYxMiA3OTJdL0NvbnRlbnRzIDUgMCBSPj5lbmRvYmoK
NCA
wIG9iajw8L1R5cGUvRm9udC9TdWJ0eXBlL1R5cGUxL0Jhc2VGb250L0hlbHZldGljYT4+ZW5kb2IKNSAw
IG9iajw8L0xlbmd0aCAyMDk+PnN0cmVhbQpCVAovRjEgMTIgVGYK
MzAgNTAwIFRkCihIZWxsbyBXb3JsZCEpIFRqCkVUCkkwIFcgMCBUcApCVAovRjEgMTAgVGYK
MzAgNDYwIFRkCihQeXRob24gaXMgYSBwb3dlcmZ1bCBwcm9ncmFtbWluZyBsYW5ndWFnZS4pIFRqCkVU
CmVuZHN0cmVhbQplbmRvYgoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDEw
IGzDADAwMDAwIGEgCjAwMDAwMDA0NyAgMDAwMDAgbiAKMDAwMDAwMDEwNCAgMDAwMDAgbiAKMDAwMDAw
MDI3MCAgMDAwMDAgbiAKMDAwMDAwMDMyOCAgMDAwMDAgbiAKdHJhaWxlcjw8L1NpemUgNi9Sb290IDEg
MCBSPj4Kc3RhcnR4cmVmCjU5MgolJUVPRge="""

def create_test_pdf_file():
    """Create a test PDF file"""
    print("[SETUP] Creating test PDF file...")
    import base64
    
    # Clean the base64 string
    pdf_data = base64.b64decode(MINIMAL_PDF_B64.replace('\n', '').replace(' ', ''))
    
    filepath = Path("test_document.pdf")
    with open(filepath, 'wb') as f:
        f.write(pdf_data)
    
    print(f"[SETUP] PDF created: {filepath} ({len(pdf_data)} bytes)")
    return filepath

def test_health():
    """Test health endpoint"""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    try:
        print("Requesting: GET /health")
        response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT)
        print(f"✓ Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_upload(filepath):
    """Test PDF upload"""
    print("\n" + "="*80)
    print("TEST 2: Upload PDF")
    print("="*80)
    
    try:
        print(f"Uploading: {filepath}")
        with open(filepath, 'rb') as f:
            files = {'file': (filepath.name, f, 'application/pdf')}
            response = requests.post(
                f"{API_BASE_URL}/upload-pdf",
                files=files,
                timeout=TIMEOUT
            )
        
        print(f"✓ Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get('success'):
            return True, data.get('session_id')
        return False, None
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def test_ask_question(session_id, question, language="en"):
    """Test asking a question"""
    print(f"\nTesting Question: '{question}' (Language: {language})")
    print("-" * 60)
    
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
        
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"✗ Error: {response.status_code}")
            try:
                print(f"Details: {response.json()}")
            except:
                print(f"Response: {response.text}")
            return False
        
        data = response.json()
        
        if data.get('success'):
            answer = data['answer'][:150] + "..." if len(data['answer']) > 150 else data['answer']
            print(f"✓ Answer: {answer}")
            return True
        else:
            print(f"✗ Failed: {data.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*80)
    print("SMART DOCUMENT ASSISTANT - COMPLETE TEST SUITE")
    print("="*80)
    
    # Create test PDF
    pdf_file = create_test_pdf_file()
    
    # Test 1: Health
    if not test_health():
        print("\n❌ Health check failed")
        return
    
    # Test 2: Upload
    success, session_id = test_upload(pdf_file)
    if not success:
        print("\n❌ Upload failed")
        return
    
    print(f"\n✓ PDF uploaded! Session: {session_id}")
    
    # Test 3: Ask questions
    print("\n" + "="*80)
    print("TEST 3: Ask Questions (English, Hindi, Marathi)")
    print("="*80)
    
    tests = [
        ("What is Python programming?", "en"),
        ("Python एक प्रोग्रामिंग भाषा है?", "hi"),
        ("Python प्रोग्रामिंग भाषा काय आहे?", "mr"),
    ]
    
    results = []
    for question, language in tests:
        time.sleep(1)
        result = test_ask_question(session_id, question, language)
        results.append((question, language, result))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for question, language, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} | {language.upper():2} | {question[:50]}")
    
    passed = sum(1 for _, _, r in results if r)
    total = len(results)
    print(f"\nResult: {passed}/{total} tests passed")
    
    # Cleanup
    pdf_file.unlink()
    print(f"\n✓ Cleanup: {pdf_file} removed")

if __name__ == "__main__":
    main()
