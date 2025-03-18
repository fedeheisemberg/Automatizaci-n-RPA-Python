import os
from PIL import Image
import pillow_heif

# Directorios de entrada y salida
input_folder = 'Sesión 4'
output_folder = 'Sesión 4 JPG'

# Crear el directorio de salida si no existe
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Función para convertir HEIC a JPG
def convert_heic_to_jpg(input_path, output_path):
    heif_image = pillow_heif.read_heif(input_path)
    image = Image.frombytes(
        heif_image.mode, 
        heif_image.size, 
        heif_image.data
    )
    image.save(output_path, "JPEG")

# Convertir todas las imágenes HEIC en la carpeta
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".heic"):
        input_path = os.path.join(input_folder, filename)
        output_filename = os.path.splitext(filename)[0] + ".jpg"
        output_path = os.path.join(output_folder, output_filename)
        
        try:
            convert_heic_to_jpg(input_path, output_path)
            print(f"Convertido: {filename} -> {output_filename}")
        except Exception as e:
            print(f"Error al convertir {filename}: {e}")

print("Conversión completada.")

