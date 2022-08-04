import pytesseract
from pdf2image import convert_from_path

class OCR:

    def __init__(self):
        self.lang = 'eng'
        self.path = None
        self.image = None
        self.text = None
        global poppler_path
        
    def set_path(self, tes_path, pop_path):
        self.path = tes_path
        pytesseract.pytesseract.tesseract_cmd = self.path
        poppler_path = pop_path

    def pdf2img(self, pdf):
        self.pdf = pdf
        images = convert_from_path(pdf, poppler_path=poppler_path)
        return images[0]
    
    def get_text(self, image, lang):
        self.image = image
        self.lang = lang
        return pytesseract.image_to_string(self.image, lang=self.lang, config='--psm 6')