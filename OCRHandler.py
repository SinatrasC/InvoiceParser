import pytesseract

class OCR:

    def __init__(self, tessaract_path):
        self.pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Emin\AppData\Local\Tesseract-OCR\tesseract.exe'
    
    def get_text(self, image, lang):
        return pytesseract.image_to_string(self.image, lang=self.lang, config='--psm 6')