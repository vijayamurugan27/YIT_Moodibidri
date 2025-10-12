from flask import Flask, request, render_template_string, redirect, url_for, flash, jsonify
import os
from werkzeug.utils import secure_filename
import PyPDF2
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Security configurations
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

# Rate limiting - CORRECTED VERSION
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Limiter correctly
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>File Upload & PDF Reader</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .alert { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .info { background: #d1ecf1; color: #0c5460; }
        .pdf-content { background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }
        .file-info { background: #e9ecef; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <h2>Upload a File & Read PDF Content</h2>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <input type="submit" value="Upload">
    </form>
    
    {% if pdf_content %}
    <div class="file-info">
        <h3>📁 File Information:</h3>
        <p><strong>Filename:</strong> {{ filename }}</p>
        <p><strong>Saved at:</strong> {{ file_path }}</p>
        <p><strong>File size:</strong> {{ file_size }} bytes</p>
    </div>
    <div class="pdf-content">
        <h3>📄 PDF Content:</h3>
        <pre>{{ pdf_content }}</pre>
    </div>
    {% endif %}
</body>
</html>
'''

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_pdf_content(filepath):
    """
    Extract text content from PDF file
    Returns: String containing PDF text content
    """
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text_content = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content += f"--- Page {page_num + 1} ---\n"
                text_content += page.extract_text() + "\n\n"
            
            return text_content if text_content.strip() else "No readable text found in PDF"
    
    except Exception as e:
        logger.error(f"Error reading PDF: {str(e)}")
        return f"Error reading PDF file: {str(e)}"

def get_file_storage_path(filename):
    """
    Generate secure file storage path
    You can modify this to organize files in subdirectories
    """
    # Option 1: Store all files in uploads folder
    base_path = app.config['UPLOAD_FOLDER']
    
    # Option 2: Organize by date (uncomment to use)
    # today = datetime.now().strftime("%Y-%m-%d")
    # date_folder = os.path.join(base_path, today)
    # os.makedirs(date_folder, exist_ok=True)
    # return os.path.join(date_folder, filename)
    
    return os.path.join(base_path, filename)

@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@app.route('/', methods=['GET'])
def upload_form():
    """Display the upload form"""
    return render_template_string(HTML_FORM)

@app.route('/', methods=['POST'])
@limiter.limit("10 per minute")  # Limit uploads to 10 per minute per IP
def upload_file():
    """Handle file upload and PDF processing"""
    try:
        # Check if file was submitted
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if file has a filename
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        # Validate file
        if file and allowed_file(file.filename):
            # Secure the filename
            filename = secure_filename(file.filename)
            
            # Generate storage path
            filepath = get_file_storage_path(filename)
            
            # Prevent overwriting existing files
            if os.path.exists(filepath):
                flash('File with this name already exists. Please rename your file.', 'error')
                return redirect(request.url)
            
            # Save the file
            file.save(filepath)
            logger.info(f"File saved successfully: {filepath}")
            
            # Get file information
            file_size = os.path.getsize(filepath)
            
            # Read PDF content if it's a PDF file
            pdf_content = ""
            if filename.lower().endswith('.pdf'):
                pdf_content = read_pdf_content(filepath)
                flash('PDF uploaded and content extracted successfully!', 'success')
            else:
                flash('File uploaded successfully!', 'success')
            
            # Display results
            return render_template_string(HTML_FORM, 
                                        pdf_content=pdf_content,
                                        filename=filename,
                                        file_path=filepath,
                                        file_size=file_size)
        else:
            allowed_types = ', '.join(ALLOWED_EXTENSIONS)
            flash(f'Invalid file type. Allowed types: {allowed_types}', 'error')
            return redirect(request.url)
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        flash('An error occurred during file upload.', 'error')
        return redirect(request.url)

@app.route('/files', methods=['GET'])
@limiter.limit("30 per minute")  # Limit file listing
def list_files():
    """API endpoint to list all uploaded files"""
    try:
        files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(filepath):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'upload_time': datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
                })
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(request.url)

@app.errorhandler(429)
def ratelimit_handler(e):
    flash('Too many upload attempts. Please try again later.', 'error')
    return redirect(request.url)

if __name__ == '__main__':
    # Install required packages: pip install flask werkzeug PyPDF2 flask-limiter
    print("📁 Upload folder location:", os.path.abspath(UPLOAD_FOLDER))
    app.run(debug=False, host='0.0.0.0', port=5000)