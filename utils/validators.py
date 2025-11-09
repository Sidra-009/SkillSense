from config import ALLOWED_EXTENSIONS

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_text_input(text: str) -> bool:
    return bool(text and text.strip())
