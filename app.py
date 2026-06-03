import os
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
from services.extractor import extract_text_from_file
from services.analyzer import analyze_resume
from services.report_generator import generate_pdf_report
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract text
            text = extract_text_from_file(filepath)
            
            if not text.strip():
                return jsonify({'error': 'Could not extract text from the file.'}), 400
            
            # Analyze text
            result = analyze_resume(text)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify(result)
            
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Allowed file types are pdf, docx'}), 400

@app.route('/api/download-report', methods=['POST'])
def download_report():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    report_filename = "Resume_Analysis_Report.pdf"
    report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
    
    try:
        generate_pdf_report(data, report_path)
        return send_file(report_path, as_attachment=True, download_name=report_filename, mimetype='application/pdf')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
