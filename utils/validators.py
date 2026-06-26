import re

def valid_amount(text):
    return bool(re.fullmatch(r"\d+(\.\d{1,2})?", text.strip()))

def valid_image_extension(filename):
    return any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png'])
