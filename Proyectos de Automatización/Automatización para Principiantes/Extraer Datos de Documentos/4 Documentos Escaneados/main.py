from azure.cognitive_services.vision.computervision import ComputerVisionClient
from azure.cognitive_services.vision.computervision.models import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import OperationStatusCodes
from PIL import Image
import time
import re
import os
from dotenv import load_dotenv
from openai import OpenAI
import convert_to_image
import csv
import json


load_dotenv()

key=os.getenv("key")
endpoint=os.getenv("endpoint")
computervision_client=ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

client=OpenAI()

def validate_image(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
            print("La imagen es válida")
            return True
    except Exception as e:
        print("La imagen no es válida")
        return False
    
def cognitive_azure_ocr(roi_name, computervision_client):
    cleaned_ocr_text = ""
    ocr_emails = []

    try:
        if not validate_image(roi_name):
            return "", []

        with open(roi_name, mode="rb") as image_data:
            read_op = computervision_client.read_in_stream(image_data, raw=True)

        operation_location = read_op.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]

        while True:
            read_results = computervision_client.get_read_result(operation_id)
            if read_results.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
                break
            time.sleep(1)
        
        if read_results.status==OperationStatusCodes.succeeded:
            ocr_text_lines=[
                line.text for page in read_results.analyze_result.read_results for line in page.lines
            ]
    
    except Exception as e:
        print(f"Error in OCR processing: {e}")
    
    return cleaned_ocr_text, ocr_emails

def extraer_datos_factura(texto_factura):
    prompt=f"""
Extrae los siguientes campos del texto proporcionado y devuelve los resultados en formato JSON:
    -Date
    -Invoice Number
    -Client
    -Subtotal
    -tax
    -Discount
    -Notes
    -term
    -Total

    Texto:
    {texto_factura}
    """
    
    response=client.chat.completions.creat(
        model="gpt-3.5-turbo",
        messages=[{"role":"system","content":"Eres un expero en análisis de texto estructurado"},{"role":"user","content":prompt}],
        max_tokens=300
    )

    #Obtener la respuesta y limpiar la cadena JSON

    datos_factura_str=response.choices[0].message.content.strip()
    datos_factura_str=datos_factura_str.replace("```json","").replace("```","").strip()

    return datos_factura_str

def add_row_csv(file_name, data):
    file_exists = os.path.isfile(file_name)

    with open(file_name, "a", newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Fecha", "Número", "Cliente", "Domicilio", "Ciudad", "NIF", "Subtotal", "IVA", "Total a pagar"])

        # Proporcionar valores predeterminados para las claves que faltan
        row = [
            data.get('Fecha', ''),
            data.get('Número', ''),
            data.get('Cliente', ''),
            data.get('Domicilio', ''),
            data.get('Ciudad', ''),
            data.get('NIF', ''),
            data.get('Subtotal', ''),
            data.get('IVA', ''),
            data.get('Total a pagar', '')
        ]

        writer.writerow(row)

def add_row_csv_errors(file_name, data):
    file_exists = os.path.isfile(file_name)

    with open(file_name, "a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Nombre factura", "Texto factura", "DatosGPT", "Error"])

        # Proporcionar valores predeterminados para evitar errores si faltan claves
        row = [
            data.get("Nombre factura", ""),
            data.get("Texto factura", ""),
            data.get("DatosGPT", ""),
            data.get("Error", "")
        ]

        writer.writerow(row)


if __name__ == "__main__":
    # Convertir el PDF a imágenes
    facturas_folder = 'facturas'
    output_folder = 'output_images'
    db_facturas = 'facturas_new.csv'
    db_errors_log = 'facturas_errors.csv'

    convert_to_image.main(facturas_folder, output_folder)

    # Listar los archivos en la carpeta facturas
    img_files = os.listdir(output_folder)
    print("Número de facturas a extraer:", len(img_files))

    for img_file in img_files:
        img_path = os.path.join(output_folder, img_file)
        clean_text, emails = cognitive_azure_ocr(img_path, computervision_client)

        # Comprobar si ha habido algún error comprobando la variable clean_text
        if clean_text == "":
            print("No se ha podido extraer texto de la imagen.")
        else:
            # Extraer los datos de la factura
            datos = extraer_datos_factura(clean_text)
            
            if datos:
                try:
                    datos_json = json.loads(datos)
                    add_row_csv(db_facturas, datos_json)
                except json.JSONDecodeError as e:
                    print(f"Error al decodificar JSON: {e}")
                    print(datos)
                    print("Factura que ha fallado la extracción de datos: ",img_file)
                    add_row_csv_errors(db_errors_log, {"Nombre factura": img_file, "Texto factura": clean_text, "DatosGPT": datos, "Error": str(e)})
            else:
                print("La respuesta de extraer datos_factura es nula.")