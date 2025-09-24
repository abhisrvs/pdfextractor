from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
import os
import re
import tempfile
from werkzeug.utils import secure_filename
import pdfplumber
import openpyxl
from openpyxl.styles import Font, PatternFill
import io
import zipfile
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_emails_from_pdf(pdf_path):
    """Extract emails and employment details (permanent/contract/remote) from PDF file using pdfplumber"""
    email_data = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Email regex pattern
                    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                    found_emails = re.findall(email_pattern, text)
                    
                    # Process each email
                    for email in found_emails:
                        # Get the context around the email (200 characters before and after for better detection)
                        email_pos = text.find(email)
                        start_pos = max(0, email_pos - 200)
                        end_pos = min(len(text), email_pos + 200)
                        context = text[start_pos:end_pos].lower()
                        
                        # Employment type keywords
                        contract_keywords = ['contract', 'contractor', 'temporary', 'temp', 'fixed term']
                        permanent_keywords = ['permanent', 'full-time', 'full time', 'perm']
                        remote_keywords = ['remote', 'work from home', 'wfh', 'virtual', 'telecommute', 'home-based']
                        
                        # Determine employment type
                        employment_type = 'Unknown'
                        if any(keyword in context for keyword in contract_keywords):
                            employment_type = 'Contract'
                        elif any(keyword in context for keyword in permanent_keywords):
                            employment_type = 'Permanent'
                            
                        # Determine if remote
                        work_location = 'On-site'
                        if any(keyword in context for keyword in remote_keywords):
                            work_location = 'Remote'
                        
                        if email not in [e[0] for e in email_data]:
                            email_data.append((email, employment_type, work_location))
    except Exception as e:
        print(f"Error extracting emails and job types: {e}")
        return []
    
    return email_data

def create_excel_file(email_data, filename="Extracted Emails"):
    """Create Excel file with extracted emails and employment details"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = filename
    
    # Add headers
    headers = ["Email Address", "Domain", "Employment Type", "Work Location", "Status"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    
    # Add email data
    for row, (email, employment_type, work_location) in enumerate(email_data, 2):
        ws.cell(row=row, column=1, value=email)
        # Extract domain
        domain = email.split('@')[1] if '@' in email else ''
        ws.cell(row=row, column=2, value=domain)
        ws.cell(row=row, column=3, value=employment_type)
        ws.cell(row=row, column=4, value=work_location)
        ws.cell(row=row, column=5, value="Valid")
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    return wb

def create_zip_file(file_data):
    """Create a ZIP file containing multiple Excel files"""
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    
    with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename, wb in file_data.items():
            # Create temporary Excel file
            temp_excel = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            wb.save(temp_excel.name)
            temp_excel.close()
            
            # Add to ZIP
            zipf.write(temp_excel.name, f"{filename}.xlsx")
            
            # Clean up temporary Excel file
            os.unlink(temp_excel.name)
    
    temp_zip.close()
    return temp_zip.name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files selected'}), 400
    
    files = request.files.getlist('files')
    
    if not files or all(file.filename == '' for file in files):
        return jsonify({'error': 'No files selected'}), 400
    
    valid_files = []
    uploaded_files = []
    
    # Validate and save files
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            uploaded_files.append(file_path)
            valid_files.append((filename, file_path))
        else:
            return jsonify({'error': f'Invalid file type: {file.filename}. Please upload PDF files only.'}), 400
    
    try:
        results = {}
        total_emails = 0
        
        # Process each file
        for filename, file_path in valid_files:
            email_data = extract_emails_from_pdf(file_path)
            if email_data:
                # Create Excel file for this PDF
                wb = create_excel_file(email_data, filename.replace('.pdf', ''))
                results[filename.replace('.pdf', '')] = wb
                total_emails += len(email_data)
        
        if not results:
            # Clean up uploaded files
            for file_path in uploaded_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
            return jsonify({'error': 'No emails found in any of the PDF files'}), 400
        
        # Create response based on number of files
        if len(results) == 1:
            # Single file - return Excel directly
            filename = list(results.keys())[0]
            wb = list(results.values())[0]
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            wb.save(temp_file.name)
            temp_file.close()
            
            # Clean up uploaded files
            for file_path in uploaded_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            return send_file(
                temp_file.name,
                as_attachment=True,
                download_name=f'{filename}_extracted_emails.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            # Multiple files - return ZIP
            zip_path = create_zip_file(results)
            
            # Clean up uploaded files
            for file_path in uploaded_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            return send_file(
                zip_path,
                as_attachment=True,
                download_name=f'extracted_emails_{len(results)}_files_{total_emails}_emails.zip',
                mimetype='application/zip'
            )
            
    except Exception as e:
        # Clean up uploaded files on error
        for file_path in uploaded_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        return jsonify({'error': f'Error processing files: {str(e)}'}), 500

@app.route('/delete_temp', methods=['POST'])
def delete_temp_file():
    """Delete temporary file after download"""
    data = request.get_json()
    file_path = data.get('file_path')
    
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
