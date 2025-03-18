from pytesseract import image_to_string
import pytesseract
import re

#Ruta a Tesseract OCR

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

img=""

text=image_to_string(img)

#Expresiones regulares para extraer la información

patterns={

}

#Diccionario para almacenar los resultados
resultados={}
#Extraer los valores usando las epxresiones regulares
for campo, patron in patterns.items():
    match=re.search(patron,text,re.IGNORECASE)
    if match:
        resultados[campo]=match.group(1)

#Mostrar resultados

for campo, valor in resultados.items():
    print(f"{campo.capitalize()}: {valor}")