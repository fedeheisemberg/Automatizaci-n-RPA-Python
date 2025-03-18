import streamlit as st
import pandas as pd
import uuid
import re
import os
import requests
from datetime import datetime
from streamlit_option_menu import option_menu
import locale
from dotenv import load_dotenv

# Carga variables de entorno
load_dotenv()

# ------------ CONFIGURACIONES --------------
page_title = "Generador de facturas"
page_icon = "📝"
layout = "wide"
euro_symbol = "\u20AC"
csv_file_path = "invoices.csv"
url_logo = "https://ibb.co/qMvcN1jf"  # URL corregida

# Configuración de la página de Streamlit
st.set_page_config(
    page_title=page_title,
    page_icon=page_icon,
    layout=layout,
    initial_sidebar_state="expanded"
)

# Ocultar elementos de Streamlit
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --------------- Inicialización de variables de estado de sesión --------------
# Inicializar las variables de estado al principio
if "expense_data" not in st.session_state:
    st.session_state.expense_data = []
if "invoice_data" not in st.session_state:
    st.session_state.invoice_data = []

# ------------------ Funciones ------------------

# Función para validar el formato de un email
def validate_email(email):
    pattern = r"[\w\.-]+@[\w\.-]+\.[\w\$]+"
    if re.match(pattern, email):
        return True
    else:
        return False

# Función para generar un ID único
def generate_uid():
    unique_id = uuid.uuid4()
    return str(unique_id)

# Función para obtener el mes y el año actual
def get_month_and_year():
    now = datetime.now()
    month = now.strftime("%B").lower()
    year = now.year
    return month, year

# Función para leer el CSV
def read_csv(file_path):
    try:
        if not os.path.exists(file_path):
            # Crear el archivo con encabezados si no existe
            with open(file_path, 'w', newline='') as f:
                f.write("from_who,to_who,logo,num_invoice,date_invoice,due_date,items,notes,term,impuesto,descuento,final_price\n")
            return []
        else:
            return pd.read_csv(file_path).values.tolist()
    except Exception as e:
        st.error(f"Error al leer el CSV: {str(e)}")
        return []

# Función para escribir en el CSV
def write_csv(file_path, data):
    try:
        df = pd.DataFrame(data, columns=["from_who", "to_who", "logo", "num_invoice", "date_invoice", "due_date", "items", "notes", "term", "impuesto", "descuento", "final_price"])
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        st.error(f"Error al escribir en el CSV: {str(e)}")
        return False

# Función para generar el PDF de la factura
def generate_invoice_pdf(from_who, to_who, logo, number, date, due_date, items, notes, terms, tax, discounts):
    invoices_directory = "invoices"
    if not os.path.exists(invoices_directory):
        os.makedirs(invoices_directory)
        
    # Incluir la API key en los headers
    api_key = "sk_H6UjYgzPrePSC4Aozptr9CuEtLx9lPxA"  # Tu API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    url = 'https://invoice-generator.com'
    
    invoice_parsed = {
        'from': from_who,
        'to': to_who,
        'logo': logo,
        'number': number,
        'currency': 'ARS',  # Usando EUR para consistencia con el símbolo euro
        'date': date,
        'due_date': due_date,
        'items': items,
        'fields': {"tax": "%", "discounts": "%", "shipping": False},
        'discounts': discounts,
        'tax': tax,
        'notes': notes,
        'terms': terms
    }
    
    try:
        r = requests.post(url, json=invoice_parsed, headers=headers)
        if r.status_code == 200 or r.status_code == 201:
            pdf = r.content
            invoice_path = f"{invoices_directory}/{number}_invoice.pdf"
            with open(invoice_path, 'wb') as f:
                f.write(pdf)
            return invoice_path
        else:
            st.error(f"Error al generar la factura: {r.text}")
            return None
    except Exception as e:
        st.error(f"Error al conectar con el servicio de facturas: {str(e)}")
        return None

# Función para enviar email (simplificada)
def send_email(to_email, invoice_path, company, invoice_number, receiver):
    st.info(f"Se simula el envío de correo a {to_email} con la factura {invoice_path}")
    st.success("En un entorno real, configura las credenciales SMTP en el archivo .env")
    return True

# --------------- Código del frontend ------------------

# --- MENÚ DE NAVEGACIÓN ---
selected = option_menu(
    menu_title=None,
    options=["Facturación", "Visualizador de datos"],
    icons=["receipt", "bar-chart-fill"],
    orientation="horizontal",
)

# Si la opción seleccionada es "Facturación"
if selected == "Facturación":
    st.title("Generador de Facturas")
    
    # Sección de información de la factura
    with st.container():
        cc1, cc2 = st.columns(2)
        cc1.image("https://via.placeholder.com/100x50?text=Logo", caption="Logo de la empresa")
        from_who = cc1.text_input("De: ", placeholder="Quién envía esta factura")
        to_who = cc1.text_input("Cobrar a: ", placeholder="Para quién es la factura")
        email = cc1.text_input("Enviar a: ", placeholder="Enviar correo (opcional)")
        if email:
            validation = validate_email(email)
            if validation == False:
                st.warning("El E-mail no tiene un formato válido.")
            else:
                st.success("La factura generada será enviada a este destinatario.")
        cc2.subheader("FACTURA")
        num_invoice = cc2.text_input("#", placeholder="Número de factura")
        date_invoice = cc2.date_input("Fecha ")
        due_date = cc2.date_input("Fecha de vencimiento ")
        payment_terms = cc2.text_input("Condiciones de pago", placeholder="Ej: Pago en 30 días")

    # Formulario para los gastos
    with st.form("entry_form", clear_on_submit=True):
        cex1, cex2, cex3 = st.columns(3)
        articulo = cex1.text_input("Artículo", placeholder="Descripción del servicio o producto")
        amount_expense = cex2.number_input("Cantidad", step=1, min_value=1)
        precio = cex3.number_input("Precio", min_value=0)
        submitted_expense = st.form_submit_button("Añadir artículo")
        if submitted_expense:
            if articulo == "":
                st.warning("Añade una descripción del artículo o servicio")
            else:
                st.success("Artículo añadido")
                st.session_state.expense_data.append({"Artículo": articulo, "Cantidad": amount_expense, "Precio": precio, "Total": amount_expense * precio})
                st.session_state.invoice_data.append({"name": articulo, "quantity": amount_expense, "unit_cost": precio})

    # Mostrar la tabla de artículos añadidos
    total_expenses = 0
    final_price = 0
    if st.session_state.expense_data:
        df_expense = pd.DataFrame(st.session_state.expense_data)
        df_expense_invoice = pd.DataFrame(st.session_state.invoice_data)
        st.subheader("Artículos añadidos")
        st.table(df_expense)
        total_expenses = df_expense["Total"].sum()
        st.text(f"Total: {total_expenses} {euro_symbol}")
        final_price = total_expenses

    # Sección de información adicional de la factura
    with st.container():
        cc3, cc4 = st.columns(2)
        notes = cc3.text_area("Notas", placeholder="Información adicional para el cliente")
        term = cc4.text_area("Términos", placeholder="Términos y condiciones de la factura")
        cc3.write(f"Subtotal: {total_expenses} {euro_symbol}")
        impuesto = cc3.number_input("Impuesto %: ", min_value=0)
        if impuesto:
            imp = 1 + (impuesto / 100)
            final_price = final_price * imp
        descuento = cc3.number_input("Descuento %: ", min_value=0)
        if descuento:
            final_price = final_price - ((descuento / 100) * final_price)
        cc3.write(f"Total: {final_price:.2f} {euro_symbol}")

    submit = st.button("Generar Factura")

    # Acciones después de enviar el formulario
    if submit:
        if not from_who or not to_who or not num_invoice or not date_invoice or not due_date:
            st.warning("Completa los campos obligatorios")
        elif len(st.session_state.expense_data) == 0:
            st.warning("Añade algún artículo")
        else:
            month, year = get_month_and_year()
            
            # 1. Guardar en CSV
            existing_data = read_csv(csv_file_path)
            new_row = [from_who, to_who, url_logo, num_invoice, str(date_invoice), str(due_date), 
                       str(st.session_state.invoice_data), notes, term, str(impuesto), str(descuento), str(final_price)]
            
            if existing_data:
                existing_data.append(new_row)
            else:
                existing_data = [new_row]
                
            if write_csv(csv_file_path, existing_data):
                st.success("Información guardada en CSV correctamente!")
            
            # 2. Generar PDF
            invoice_path = generate_invoice_pdf(
                from_who, to_who, url_logo, num_invoice, str(date_invoice), str(due_date), 
                st.session_state.invoice_data, notes, term, impuesto, descuento
            )
            
            if invoice_path:
                with open(invoice_path, 'rb') as file:
                    st.success("Factura generada correctamente!")
                    st.download_button(
                        label="Descargar factura", 
                        data=file, 
                        file_name=f"{num_invoice}_invoice.pdf", 
                        mime="application/pdf"
                    )
                
                # 3. Enviar por email si hay dirección
                if email and validate_email(email):
                    if send_email(email, invoice_path, from_who, num_invoice, to_who):
                        st.success(f"Se ha enviado la factura a {email}")

# Si la opción seleccionada es "Visualizador de datos"
elif selected == "Visualizador de datos":
    st.title("Visualizador de datos")
    
    try:
        if os.path.exists(csv_file_path):
            df = pd.read_csv(csv_file_path)
            if not df.empty:
                st.subheader("Facturas registradas")
                st.dataframe(df)
                
                # Análisis básico
                st.subheader("Resumen")
                total_facturas = len(df)
                total_ingresos = df['final_price'].astype(float).sum() if 'final_price' in df.columns else 0
                
                col1, col2 = st.columns(2)
                col1.metric("Total de facturas", total_facturas)
                col2.metric("Total de ingresos", f"{total_ingresos:.2f} {euro_symbol}")
            else:
                st.info("No hay datos de facturas registrados todavía.")
        else:
            st.info("No se encontró el archivo CSV. Crea facturas primero.")
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")