import google.generativeai as genai
from decouple import config
from PIL import Image
import json

genai.configure(api_key=config("gemini_api"))

def extract_text_from_image(image):
    """Extracts the details from the ID image"""
    opened_image = Image.open(image)
    model = genai.GenerativeModel("gemini-1.5-flash")
    result = model.generate_content(
        [opened_image, "\n\n", """
            extract text from the image provided and return a json format
            eg.
                {
                    "student_name": "names extracted",
                    "reg_no": "student registration number",
                    "course" : student course,
                    "is_id": "true or false based on ai",
                    "is_egerton": "true or false based on university written at top"
                }
         """]
    )
    
    # Remove the backticks and JSON formatting
    result_text = result.text.strip().strip('```json').strip('```')
    
    # Parse the result text into a Python dictionary
    try:
        result_dict = json.loads(result_text)
    except json.JSONDecodeError:
        print("Failed to parse JSON response from AI")
        return None
    return result_dict

def allowed_file_format(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', "webp"}


