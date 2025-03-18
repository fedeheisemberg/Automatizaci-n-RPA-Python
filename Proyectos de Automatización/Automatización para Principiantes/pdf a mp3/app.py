import pyttsx3
from PyPDF2 import PdfFileReader

with open('guion.pdf','rb') as file:
    pdfreader = PdfFileReader(file)
    text = ''
    for page_num in range(len(pdfreader.pages)):
        page = pdfreader.getPage(page_num)
        text += page.extract_text()

speaker=pyttsx3.init()
speaker.save_to_file(text,'audio.mp3')
speaker.runAndWait()
speaker.stop()