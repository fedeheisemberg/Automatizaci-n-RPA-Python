import pywhatkit

import pywhatkit as kit
import datetime

# 1️⃣ Enviar mensaje de WhatsApp (programado para dentro de 2 minutos)
now = datetime.datetime.now()
kit.sendwhatmsg("+5491112345678", "Hola, esto es un mensaje automatizado con PyWhatKit!", 
                now.hour, now.minute + 2)

# 2️⃣ Enviar imagen a un contacto/grupo de WhatsApp
kit.sendwhats_image("+5491112345678", "imagen.jpg", "Aquí tienes una imagen!")

# 3️⃣ Buscar en Google
kit.search("Qué es la inteligencia artificial")

# 4️⃣ Reproducir un video en YouTube
kit.playonyt("Python tutorial para principiantes")

# 5️⃣ Obtener información de Wikipedia
wikipedia_info = kit.info("Elon Musk", 3)  # Resumen con 3 líneas
print("\n🔍 Información de Wikipedia sobre Elon Musk:\n", wikipedia_info)

# 6️⃣ Convertir texto a manuscrito
kit.text_to_handwriting("Hola, este es un texto convertido a manuscrito con PyWhatKit!", 
                        rgb=[0, 0, 255])

# 7️⃣ Dibujar una imagen en ASCII art
kit.image_to_ascii_art("imagen.jpg", "ascii_art.txt")

# 8️⃣ Resolver operaciones matemáticas simples
kit.solve_equation("2x + 5 = 15")  # Devuelve el valor de x

# 9️⃣ Imprimir el historial de eventos realizados con pywhatkit
kit.show_history()
