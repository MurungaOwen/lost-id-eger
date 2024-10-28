import google.generativeai as genai
from decouple import config
from PIL import Image
import json

genai.configure(api_key=config("gemini_api"))

def extract_text_from_image(image):
    """Extracts the details from the ID image"""
    opened_image = Image.open(image)
    model = genai.GenerativeModel("gemini-1.5-flash")

    try:
        result = model.generate_content(
            [opened_image, "\n\n", """
                Extract text from the image provided and return a json format
                Example output:
                {
                    "student_name": "names extracted",
                    "reg_no": "student registration number",
                    "course": "student course",
                    "is_id": true or false,
                    "is_egerton": true or false
                }
            """]
        )
        
        response_text = result.text.strip().strip('```json').strip('```')
        print("Cleaned AI response:", response_text)
        
        try:
            result_dict = json.loads(response_text)
            print("Parsed JSON:", result_dict)
            return result_dict
        except json.JSONDecodeError as e:
            print("Failed to parse JSON:", e)
            return None

    except Exception as e:
        print(f"An error occurred during text extraction: {e}")
        return None


def allowed_file_format(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', "webp"}
