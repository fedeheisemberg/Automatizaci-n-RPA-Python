import streamlit as st
from PIL import Image
from rembg import remove
import io
import os

#Funciones

def process_image(image_uploaded):
    image=Image.open(image_uploaded)
    proccesed_image=remove_background(image)
    return proccesed_image

def remove_background(image):
    image.byte=io.BytesIO()
    image.save(image_byte,format='PNG')
    image_byte.seek(0)
    procceesed_image_bytes=remove(image_byte.read())
    return Image.open(io.BytesIO(procceesed_image_bytes))


#Front

st.image("assets/remove-background.png")
st.header('Background Removal App')
st.subheader('Sube una imagen y elimina el fondo')
uploaded_image=st.file_uploader("Sube una imagen",type=['png','jpg','jpeg'])

if uploaded_image is not None:
    st.image(uploaded_image,caption='Imagen Original',use_column_width=True)
    
    remove_button=st.button(label='Eliminar fondo')

    if remove_button:

        proccesed_image=process_image(uploaded_image)
        st.image(proccesed_image,caption='Imagen Procesada',use_column_width=True)
        proccesed_image.save('proccesed_image.png')
        with open('proccesed_image.png','rb') as file:
            proccesed_image_data=file.read()

        st.download_button(label='Descargar Imagen Procesada',data=proccesed_image_data,file_name='proccesed_image.png',mime='image/png')
        os.remove(proccesed_image.png)

