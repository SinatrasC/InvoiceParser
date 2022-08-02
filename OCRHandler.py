import pytesseract
from pdf2image import convert_from_path

class OCR:

    def __init__(self):
        self.lang = 'eng'
        self.path = None
        self.image = None
        self.text = None
        
    def set_path(self, path):
        self.path = path
        pytesseract.pytesseract.tesseract_cmd = self.path

    def pdf2img(self, pdf):
        self.pdf = pdf
        poppler_path = r'C:\Users\Emin\poppler-22.04.0\Library\bin'
        images = convert_from_path(pdf, poppler_path=poppler_path)
        return images[0]
    
    def get_text(self, image, lang):
        self.image = image
        self.lang = lang
        return pytesseract.image_to_string(self.image, lang=self.lang, config='--psm 6')