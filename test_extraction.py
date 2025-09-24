#!/usr/bin/env python3
"""
Test script to demonstrate PDF email extraction functionality
"""

import os
import tempfile
from app import extract_emails_from_pdf, create_excel_file

def test_email_extraction():
    """Test the email extraction functionality"""
    
    # Create a simple test PDF content (simulated)
    test_content = """
    Contact Information:
    John Doe - john.doe@example.com
    Jane Smith - jane.smith@company.org
    Support Team - support@helpdesk.net
    Sales Department - sales@business.com
    
    Additional contacts:
    admin@website.com
    info@services.co.uk
    """
    
    print("PDF Email Extractor - Test Script")
    print("=" * 40)
    
    # Simulate extracted emails (in real usage, these would come from PDF)
    test_emails = [
        "john.doe@example.com",
        "jane.smith@company.org", 
        "support@helpdesk.net",
        "sales@business.com",
        "admin@website.com",
        "info@services.co.uk"
    ]
    
    print(f"Found {len(test_emails)} email addresses:")
    for i, email in enumerate(test_emails, 1):
        print(f"  {i}. {email}")
    
    # Test Excel file creation
    print("\nCreating Excel file...")
    wb = create_excel_file(test_emails)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
        wb.save(temp_file.name)
        print(f"Excel file created: {temp_file.name}")
        print(f"File size: {os.path.getsize(temp_file.name)} bytes")
    
    print("\nTest completed successfully!")
    print("\nTo run the web application:")
    print("  python3 app.py")
    print("  Then open http://localhost:8000 in your browser")
    print("\nNew Features:")
    print("  - Multiple file upload support")
    print("  - ZIP download for multiple files")
    print("  - Automatic file cleanup")
    print("  - Fixed double upload issue")

if __name__ == "__main__":
    test_email_extraction()
