from docling.document_converter import DocumentConverter

source="D:\Users\User\Documents\Archivos Python VSCODE\Proyectos de Automatización\Automatización para Principiantes\Extraer Datos de Documentos\1 Documentos Estructurados\Extractor de Facturas\invoices"
converter=DocumentConverter()
result=converter.convert(source)    

#Exportar el resultado a un diccionario

data=result.document.export_to_dict()

#Función para extraer el valor del texto específico

def extract_value(texts,key):
    for i, item in enumerate(texts):
        if item['text']==key and i + 1<len(texts):
            return texts[i+1]['text']
    return None

#Extraer los números de factura, orden, fecha, fecha de vencimiento y total.

invoice_number=extract_value(data['texts'],"Invoice Number")
order_number=extract_value(data['texts'],"Order Number")
due_date=extract_value(data['texts'],"Due Date")
total_due=extract_value(data['texts'],"Total Due")
from_how= extract_value(data['texts'],"From")
to= extract_value(data['texts'],"To")

#Mostrar los resultados
print("Invoice Number:",invoice_number)
print("Order Number:",order_number)
print("Due Date:",due_date)
print("Total Due:",total_due)
print("From:",from_how)
print("To:",to)
