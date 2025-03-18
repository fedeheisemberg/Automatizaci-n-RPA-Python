import PyPDF2
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

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

def extract_invoice_info(pdf_file_path):

    #Abrir el archivo PDF

    with open(pdf_file_path,"rb") as file:
        pdf_reader=PyPDF2.PdfFileReader(file)
        text=""
        for page_num in range(len(pdf_reader.pages)):
            page=pdf_reader.pages[page_num]
            text+=page.extract_text()

        #Extraer los datos de la factura
        datos_factura_str=extraer_datos_factura(text)
        datos_factura=json.loads(datos_factura_str)

        #Extraer información de la factura
        invoice_number=datos_factura.get("Invoice Number")
        bill_to=datos_factura.get("Client")
        subtotal=datos_factura.get("Subtotal")
        total=datos_factura.get("Total")
        discount=datos_factura.get("Discount")
        tax=datos_factura.get("tax")
        notes=datos_factura.get("Notes")
        terms=datos_factura.get("term")

        return invoice_number,bill_to,subtotal,total,discount,tax,notes,terms
    
def get_files_in_folder(folder_path):
    files=[]
    for root,dirs,filenames in os.walk(folder_path):
        for filename in filenames:
            files.append(os.path.join(root,filename))
    return files

if __name__=="__main__":

    folder_path='documents'
    files=get_files_in_folder(folder_path)

    print("files:",files)
    invoice_number,bill_to,subtotal,total,discount,tax,notes,terms=extract_invoice_info(files)

    #Imprimir los resultados
    print("Invoice Number:",invoice_number)
    print("Bill To:",bill_to)
    print("Subtotal:",subtotal)
    print("Total:",total)
    print("Discount:",discount)
    print("Tax:",tax)
    print("Notes:",notes)
    print("Terms:",terms)

    #Mover el archivo a la carpeta de facturas procesadas
    processed_folder_path="processed_documents"
    os.makedirs(processed_folder_path,exist_ok=True)
    new_file_path=os.path.join(processed_folder_path,os.path.basename(files))
    os.rename(files,new_file_path)
