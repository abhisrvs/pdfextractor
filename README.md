# PDF Email Extractor

A modern web application that extracts email addresses from PDF files and exports them to Excel format.

## Features

- 📄 Upload multiple PDF files via drag & drop or file browser
- 📧 Extract all email addresses from PDF content
- 📊 Export results to Excel (.xlsx) format with organized columns
- 📦 ZIP download for multiple files
- 🗑️ Automatic file cleanup after processing
- 🎨 Modern, responsive UI with Bootstrap
- 🔒 Secure file processing
- ⚡ Fast and efficient processing
- 🚫 Fixed double upload issue

## Installation

1. **Clone or download this repository**
   ```bash
   cd fextract
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:8000`

3. **Upload PDF files**
   - Drag and drop one or more PDF files onto the upload area, or
   - Click "Choose Files" to browse and select multiple PDF files
   - Remove individual files using the X button if needed

4. **Download results**
   - Click "Extract Emails" to process all files
   - Single file: Downloads Excel file directly
   - Multiple files: Downloads ZIP file containing separate Excel files for each PDF
   - All uploaded files are automatically cleaned up after processing

## Excel Output Format

The exported Excel file contains:
- **Email Address**: The complete email address
- **Domain**: The domain part of the email
- **Status**: Validation status (currently shows "Valid")

## Technical Details

- **Backend**: Flask (Python web framework)
- **PDF Processing**: pdfplumber (extracts text from PDFs)
- **Excel Export**: openpyxl (creates Excel files)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **File Upload**: Secure file handling with validation

## Requirements

- Python 3.7+
- Modern web browser
- PDF files with extractable text (not scanned images)

## File Structure

```
fextract/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── templates/
│   └── index.html     # Main web interface
└── uploads/           # Temporary file storage (created automatically)
```

## Error Handling

The application includes comprehensive error handling for:
- Invalid file types (non-PDF files)
- Corrupted or unreadable PDF files
- Files without extractable text
- Network and processing errors

## Security Features

- File type validation
- Secure filename handling
- Temporary file cleanup
- Input sanitization

## License

This project is open source and available under the MIT License.
