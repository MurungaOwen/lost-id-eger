from flask import Flask, request, jsonify
import uuid
from werkzeug.utils import secure_filename
from lib.db import SupabaseDb
from utils import allowed_file_format,extract_text_from_image

app = Flask(__name__)
supabase_db = SupabaseDb()

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    contact = request.form.get('contact')

    
    # If the user does not select a file, the browser submits an empty part without filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    extracted_data = extract_text_from_image(file)
    reg_no = extracted_data.get('reg_no')
    student_name = extracted_data.get('reg_no')
    is_id = extracted_data.get('is_id')
    course = extracted_data.get('course')
    is_egerton = extracted_data.get('is_egerton')

    if is_egerton == "false":
        return jsonify({"error": "ID you provided is not of Egerton university"}), 400
    
    if is_id == "false":
        return jsonify({"error": "Please upload an id image"}), 400
    
    if file and allowed_file_format(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"  # Generate unique filename

        bucket_name = "lost-id-images"
        public_url = supabase_db.upload_id_image(file, bucket_name, unique_filename)
        
        if public_url and supabase_db.insert("lostId", {
            "image_url": public_url,
            "contact": contact,
            "reg_no": reg_no,
            "student_name": student_name,
            "course": course
        }):
            return jsonify({"message": "File uploaded successfully", "url": public_url}), 200
        else:
            return jsonify({"error": "Failed to upload file"}), 500

    return jsonify({"error": "File type not allowed"}), 400

@app.route('/list', methods=['GET'])
def list_all_ids():
    all_ids = supabase_db.select_all("lostId")
    return jsonify(all_ids), 200

@app.route('/search', methods=['GET'])
def search():
    reg_no = request.args.get('reg_no')
    results = supabase_db.select_with_filter("lostId", "reg_no", reg_no)
    if results:
        return jsonify(results), 200
    return jsonify({"error": "Not found"}), 200

@app.route("/sort", methods=['GET'])
def complex_queries():
    # results = supabase_db.db.table("lostId").select("*").
    pass

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
