import os
from email.message import EmailMessage
import ssl
import smtplib
import imghdr

email_emisor = ""
email_receptor = ""
email_contrasena=os.environ.get('EMAIL_PASSWORD')

asunto="Presentación y Envío de CV"
cuerpo="""
Estimado/a equipo de Recursos Humanos,

Mi nombre es Federico Luis Martínez. Soy estudiante avanzado de la Licenciatura en Administración de Empresas en la Universidad de Congreso y cuento con conocimientos en análisis de datos, automatización de procesos (RPA) y gestión de información. 

Adjunto mi CV para su consideración y quedo a disposición para conversar sobre posibles oportunidades en su empresa.

Agradezco su tiempo y espero su respuesta.

Saludos cordiales,
Federico Luis Martínez: """


em=EmailMessage()
em['From']=email_emisor
em['To']=email_receptor
em['Subject']=asunto
em.set_content(cuerpo)

#Adjuntar archivo

with open('Profile Photo.jpeg','rb') as file:
    file_data=file.read()
    file_tipo=imghdr.what(file.name)
    file_nombre=file.name

em.add_attachment(file_data, maintype='image', subtype=file_tipo, filename=file_nombre)

with open('Federico Martinez Portfolio CV 2025 - Marzo 2025.pdf','rb') as file:
    file_data=file.read()
    file_tipo='pdf'
    file_nombre=file.name
em.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_nombre)

contexto=ssl.create_default_context()
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
    smtp.login(email_emisor, email_contrasena)
    smtp.sendmail(email_emisor, email_receptor, em.as_string())
    print("Correo enviado con éxito")