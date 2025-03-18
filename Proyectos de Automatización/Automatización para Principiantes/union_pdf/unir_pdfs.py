import streamlit as st
from PyPDF2 import PdfFileMerger
import os

#VARIABLES

output_pdf="documents/pdf_final.pdf"

#FUNCIONES

def unir_pdfs(output_path,documents):
    pdf_final=PyPDF2.PdfFileMerger()

    for document in documents:
        pdf_final.append(document) #Añadir pdfs al pdf final

    pdf_final.write(output_path) #Guardar el pdf final
#---- FRONT---

st.image("assets/combine-pdf.png")
st.header('Unir pdfs')
st.subheader('Adjuntar pdfs para unir')

pdf_adjuntos=st.file_uploader("Adjuntar pdfs", type=['pdf'], accept_multiple_files=True)

unir=st.button("Unir pdfs")

if unir:
    if len(pdf_ajuntos)<=1:
        st.warning('Adjunta al menos dos pdfs')
    else:
        unir_pdfs(output_pdf,pdf_adjuntos)
        st.success('Pdfs unidos correctamente, descarga el pdf final.')
        with open(output_pdf,'rb') as file:
            pdf_data=file.read()
        st.download_button(label='Descargar pdf final',data=pdf_data,file_name='pdf_final.pdf',mime='application/pdf') 