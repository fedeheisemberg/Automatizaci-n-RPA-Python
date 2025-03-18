import PyPDF2
import os
import re
import uuid
import pandas as pd

def extract_invoice_info(pdf_file_path):
    """Extrae información clave de una factura en PDF."""
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = '\n'.join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

    patterns = {
        "Invoice Number": r'INVOICE\s*#\s*([\d-]+)',
        "Bill To": r'Bill\s*To\s*:\s*([\w\s]+)',
        "Items": r'(?!Item\sQuantity\sRate\sAmount)([\w\s]+?)\s+(\d+)\s+ARS\s+([\d,.]+)\s+ARS\s+([\d,.]+)',
        "Notes": r'Notes\s*:\s*(.+?)(?=\n[A-Z]|$)',
        "Payment Terms": r'Método de pago\s*:\s*([\w\s]+)',
        "CUITs": r'CUIT\s*Emisor\s*:\s*(\d{11})\s*CUIT\s*Receptor\s*:\s*(\d{11})',
        "Discount & Tax": r'Discount\s*\((\d+)%\)[\s\S]*?Tax\s*\((\d+)%\)'
    }
    
    extracted_data = {"ID": str(uuid.uuid4())}
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if key == "Items":
            extracted_data[key] = re.findall(pattern, text)
        elif key == "CUITs":
            extracted_data["CUIT Emisor"], extracted_data["CUIT Receptor"] = match.groups() if match else (None, None)
        elif key == "Discount & Tax":
            extracted_data["Discount"], extracted_data["Tax"] = match.groups() if match else (None, None)
        else:
            extracted_data[key] = match.group(1).strip() if match else None

    subtotal = sum(float(item[3].replace(',', '')) for item in extracted_data.get("Items", []))
    discount_percentage = int(extracted_data.get("Discount", 0))
    tax_percentage = int(extracted_data.get("Tax", 0))
    total_after_discount = subtotal * (1 - discount_percentage / 100)
    total = total_after_discount * (1 + tax_percentage / 100)

    extracted_data.update({"Subtotal": subtotal, "Total": total})
    return extracted_data

def process_invoices_to_excel(folder_path, output_file):
    files = [os.path.join(root, f) for root, _, filenames in os.walk(folder_path) for f in filenames if f.lower().endswith(".pdf")]
    
    data_list = []
    for file in files:
        invoice_data = extract_invoice_info(file)
        data_list.append(invoice_data)
    
    df = pd.DataFrame(data_list)
    df.to_excel(output_file, index=False, startrow=1)
    print(f"✅ Datos exportados a {output_file}")

if __name__ == "__main__":
    invoices_dir = r"D:\\Users\\User\\Documents\\Archivos Python VSCODE\\Proyectos de Automatización\\Automatización para Principiantes\\Extractor de Facturas\\invoices"
    output_excel = "invoices_data.xlsx"
    process_invoices_to_excel(invoices_dir, output_excel)
