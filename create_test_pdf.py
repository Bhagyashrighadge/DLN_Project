#!/usr/bin/env python3
"""
Create a valid test PDF file
"""

try:
    # Try to use fpdf2 if available
    from fpdf import FPDF
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    content = """
Welcome to the Smart Document Assistant Test

This document contains sample text for testing the RAG system.

What is Python?
Python is a high-level, interpreted programming language created by Guido van Rossum. It emphasizes code readability and supports multiple programming paradigms.

Key Features:
- Easy to learn and read syntax
- Object-oriented and functional programming
- Extensive standard library  
- Cross-platform compatibility
- Dynamic typing

Python in Hindi:
Python एक उच्च-स्तरीय, व्याख्या की जाने वाली प्रोग्रामिंग भाषा है जो कोड की पठनीयता पर जोर देती है।

Python in Marathi:
Python एक शक्तिशाली प्रोग्रामिंग भाषा आहे जी शिकणे सोपे आहे.

Applications:
Python is used in web development, data analysis, artificial intelligence, scientific computing, and many more domains.
"""
    
    for line in content.split('\n'):
        if line.strip():
            pdf.cell(200, 10, txt=line[:80], ln=True)
    
    pdf.output("test_document.pdf")
    print("✓ Valid PDF created: test_document.pdf")
    
except ImportError:
    print("fpdf2 not available, trying reportlab...")
    try:
        from reportlab.pdfgen import canvas
        from io import BytesIO
        
        c = canvas.Canvas("test_document.pdf")
        c.setFont("Helvetica", 12)
        
        y = 750
        lines = [
            "Welcome to the Smart Document Assistant Test",
            "",
            "This document contains sample text for testing the RAG system.",
            "",
            "What is Python?",
            "Python is a high-level programming language created by Guido van Rossum.",
            "It emphasizes code readability and supports multiple programming paradigms.",
            "",
            "Python Features:",
            "- Easy to learn and read syntax",
            "- Object-oriented and functional programming",
            "- Extensive standard library",
            "- Cross-platform compatibility",
            "",
            "Python in Hindi: Python एक उच्च-स्तरीय प्रोग्रामिंग भाषा है।",
            "Python in Marathi: Python एक शक्तिशाली प्रोग्रामिंग भाषा आहे।",
            "",
            "Python is widely used in web development, data analysis, AI, and scientific computing."
        ]
        
        for line in lines:
            c.drawString(50, y, line)
            y -= 20
        
        c.save()
        print("✓ Valid PDF created: test_document.pdf")
        
    except ImportError:
        print("✗ Neither fpdf2 nor reportlab available")
        print("Please install: pip install fpdf2")
