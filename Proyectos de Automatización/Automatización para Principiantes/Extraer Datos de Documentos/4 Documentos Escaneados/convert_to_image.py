import os
import fitz  # PyMuPDF

def pdf_to_images(pdf_path, output_folder):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Get the file name without the extension
    file_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate through each page
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()

        # Save the image
        output_path = os.path.join(output_folder, f'{file_name}_page_{page_num + 1}.png')
        pix.save(output_path)
        # print(f'Saved: {output_path}')

def main(input_folder,output_folder):
    #listar los archivos en la carpeta facturas
    pdf_files=os.listdir(input_folder)

    for pdf_file in pdf_files:
        pdf_path=os.path.join(input_folder,pdf_file)
        pdf_to_images(pdf_path,output_folder)