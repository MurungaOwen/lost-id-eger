from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from io import BytesIO
from werkzeug.utils import secure_filename
from lib.db import SupabaseDb
from utils import allowed_file_format,extract_text_from_image

app = Flask(__name__)
CORS(app)
supabase_db = SupabaseDb()

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        file = request.files['file']
        contact = request.form.get('contact')
        # If the user does not select a file, the browser submits an empty part without filename
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        extracted_data = extract_text_from_image(file)
        if not extracted_data:
            return jsonify({"error": "Error extracting data from image"}), 500
        reg_no = extracted_data.get('reg_no')
        student_name = extracted_data.get('student_name')
        is_id = extracted_data.get('is_id')
        course = extracted_data.get('course')
        is_egerton = extracted_data.get('is_egerton')

        if not is_id:
            return jsonify({"error": "Please upload an id image"}), 400
        
        # elif not is_egerton:
        #     return jsonify({"error": "ID you provided is not of Egerton university"}), 400
        
        elif file and allowed_file_format(file.filename) and extracted_data:
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
                print("haiwezi: {}".format(public_url))
                return jsonify({"error": "Failed to upload file"}), 500
        else:
            return jsonify({"error": "File type not allowed"}), 400
    except ValueError as e:
        return jsonify({"error": e})
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
    # results = supabase_db.db.table("lostId").select("*")
    pass

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
