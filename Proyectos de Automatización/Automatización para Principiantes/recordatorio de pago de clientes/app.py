import csv
from datetime import datetime
from send_email import send_email
from send_sms import send_sms

csv_filename = "client_information.csv"
sender="Optima - Consulting & Management LLC"

with open(csv_filename,'r') as csv_file:
    reader=csv.DictReader(csv_file)
    for row in reader:
        current_date=datetime.now().strftime('%Y-%m-%d')
        next_payment_date=row['Next Payment']
        last_payment_date=row['Last Payment']

        if next_payment_date<current_date:
            client_name=row['Name']
            client_email=row['Email']
            client_phone_number=row['Phone Number']
            payment_period=row['Payment Period']

            sms_message=f"Hola {client_name}, este es un recordatorio de que tu pago vence hoy. Por favor realiza tu pago lo antes posible."

            #Enviar SMS

            send_sms(sms_message,client_phone_number)
            #Enviar correo
            send_email(sender,client_email,client_name,last_payment_date,next_payment_date,payment_period)
            print(f"Recordatorio de pago enviado a {client_name}")