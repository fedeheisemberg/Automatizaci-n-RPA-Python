#send_email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
import os
from dotenv import load_dotenv
from email import encoders
import streamlit as st
import datetime  

def send(to_email, invoice_path, company, invoice_number, receiver):
    try:
        send_email(to_email, invoice_path, company, invoice_number, receiver)
        return True
    except Exception as e:
        st.error(f"Error al enviar el correo: {str(e)}")
        return False

def send_email(to_email, invoice, company, invoice_number, receiver):
    load_dotenv()
    
    # Create the email message
    msg = MIMEMultipart()
    
    #Alternative css
    css_style_alternative = """
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333333;
            max-width: 650px;
            margin: 0 auto;
        }
        .header {
            background-color: #4285f4;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .content {
            padding: 20px;
            background-color: #f9f9f9;
        }
        .footer {
            background-color: #eeeeee;
            padding: 15px;
            text-align: center;
            font-size: 12px;
            color: #666666;
        }
        .important {
            color: #d62d20;
            font-weight: bold;
        }
        .details {
            margin: 20px 0;
            border: 1px solid #dddddd;
            padding: 15px;
            background-color: white;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 10px;
            border-bottom: 1px solid #dddddd;
            text-align: left;
        }
    """

    html_mensaje = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Factura {invoice_number}</title>
        <style>
            {css_style_alternative}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Factura #{invoice_number}</h1>
        </div>
        <div class="content">
            <p>Estimado/a <strong>{receiver}</strong>,</p>
            
            <p>Adjunto encontrará la factura #{invoice_number} correspondiente a los servicios prestados para <strong>{company}</strong>.</p>
            
            <div class="details">
                <h2>Detalles de la factura:</h2>
                <table>
                    <tr>
                        <th>Número de factura</th>
                        <td>{invoice_number}</td>
                    </tr>
                    <tr>
                        <th>Empresa</th>
                        <td>{company}</td>
                    </tr>
                    <tr>
                        <th>Documento</th>
                        <td>{invoice}</td>
                    </tr>
                </table>
            </div>
            
            <p class="important">Por favor revise el documento adjunto para más detalles.</p>
            
            <p>Si tiene alguna pregunta o inquietud sobre esta factura, no dude en contactarnos respondiendo a este correo electrónico.</p>
            
            <p>Atentamente,<br>
            El equipo de facturación</p>
        </div>
        <div class="footer">
            <p>Este es un correo electrónico automático. Por favor no responda directamente a esta dirección.</p>
            <p>© {company} - {datetime.datetime.now().year}</p>
        </div>
    </body>
    </html>
    """
    
    # Attach the HTML content to the email
    msg.attach(MIMEText(html_mensaje, 'html'))
    
    # Attach the file
    with open(invoice, 'rb') as file:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=invoice)
        msg.attach(part)
    
    # SMTP server configuration
    smtp_server = 'smtp.gmail.com'
    #smtp_server = "smtp-mail.outlook.com"
    smtp_port = 587
    smtp_username = os.getenv('smtp_username')
    smtp_password = os.getenv('smtp_password')

    # Email configuration
    sender_email = f'Equipo {company}'
    subject = f'{receiver} - Factura {invoice_number}'
    msg['From'] = sender_email
    msg['Subject'] = subject

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        # Send the email
        msg['To'] = to_email
        server.sendmail(sender_email, to_email, msg.as_string())
        
        server.quit()

    except smtplib.SMTPException as e:
        st.exception("There was an error sending the email with your information to rindus expenses management, please try later or contact with the administrator.")