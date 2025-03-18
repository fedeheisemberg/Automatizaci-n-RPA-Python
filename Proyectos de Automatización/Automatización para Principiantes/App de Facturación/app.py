#app.py
import streamlit as st  # pip install streamlit
from datetime import datetime
import pandas as pd
import uuid
import re
from class_csv import CSVFile
from google_sheets import GoogleSheet
from class_invoice_pdf import ApiConnector
from send_email import send

import google_auth_oauthlib.flow as flow

# Otros imports
import os
from streamlit_elements import Elements
from streamlit_option_menu import option_menu  # pip install streamlit-option-menu
import locale

# ------------ CONFIGURACIONES --------------

page_title = "Generador de facturas"
page_icon = "📝"  # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "wide"
euro_symbol = "\u20AC"
total_expenses = 0
final_price = 0
df_expense = ""
css = "style/main.css"
file_name_gs = ""
google_sheet = ""
sheet_name = ""
to_email = ""
sender = "Negocio***"
code = ""
scope = ""
csv = "invoices.csv"
logo = "logo "
file_authentication_gs = "invoice-tool-authentication.json"
google_sheet = "invoice-tool"
sheet_name = "invoices"
url_logo = "https://ibb.co/qMvcN1jf"

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Ex-Stream-ly Cool App",
    page_icon=page_icon,
    layout=layout,
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': 'https://www.extremelycoolapp.com/bug',
        'About': "# This is a header. This is an *extremely* cool app!"
    }
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

# ------------------ Funciones ------------------

# Función para cargar CSS local
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Función para validar el formato de un email
def validate_email(email):
    pattern = r"[\w\.-]+@[\w\.-]+\.[\w\$]+"
    if re.match(pattern, email):
        return True
    else:
        return False

# Función para generar un ID único
def generate_uid():
    unique_id = uuid.uuid4()  # Genera un UUID
    unique_id_str = str(unique_id)  # Convierte el UUID a string
    return unique_id_str

# Función para obtener el mes y el año actual en español
def get_month_and_year():
    locale.setlocale(locale.LC_TIME, 'es_ES')  # Configura el locale a español
    now = datetime.now()
    month = now.strftime("%B").lower()  # Obtiene el nombre del mes en minúsculas
    year = datetime.now().year  # Obtiene el año actual
    return month, year

# --------------- Variables de estado de sesión --------------

# Inicializa el estado de sesión para la primera vez
if "first_time" not in st.session_state:
    st.session_state.first_time = ""
    # google = GoogleSheet(file_name_gs, google_sheet, sheet_name)
    # obtener información

# Inicializa el estado de sesión para los ítems de la factura
if "items" not in st.session_state:
    st.session_state.items_invoice = []

# --------------- Código de inicio de sesión ---------------------

# --------------- Código del frontend ------------------

# --- MENÚ DE NAVEGACIÓN ---
selected = option_menu(
    menu_title=None,
    options=["Facturación", "Visualizador de datos"],
    icons=["receipt", "bar-chart-fill"],  # https://icons.getbootstrap.com/
    orientation="horizontal",
)

# Si la opción seleccionada es "Facturación"
if selected == "Facturación":

    # Sección de información de la factura
    with st.container():
        cc1, cc2 = st.columns(2)
        cc1.image("assets/logo.PNG", caption="Valerapp", width=100)
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
        cc2.text_input("Condiciones de pago")
        # cc2.text_input("Orden de compra")

    # Formulario para los gastos
    with st.form("entry_form", clear_on_submit=True):
        if "expense_data" not in st.session_state:
            st.session_state.expense_data = []
        if "invoice_data" not in st.session_state:
            st.session_state.invoice_data = []
        if "files" not in st.session_state:
            st.session_state.files = []

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

        # Mostrar la tabla de costos de transporte
        if st.session_state.expense_data:
            df_expense = pd.DataFrame(st.session_state.expense_data)
            df_expense_invoice = pd.DataFrame(st.session_state.invoice_data)
            st.subheader("Artículos añadidos")
            st.table(df_expense)
            total_expenses = df_expense["Total"].sum()
            st.text(f"Total: {total_expenses}" + " " + euro_symbol)
            # Convertir el DataFrame a un array de objetos
            st.session_state.items_invoice = df_expense.to_dict('records')
            st.session_state.invoice_data = df_expense_invoice.to_dict('records')
            final_price = total_expenses

        # Sección de información adicional de la factura
        with st.container():
            cc3, cc4 = st.columns(2)
            notes = cc3.text_area("Notas")
            term = cc4.text_area("Términos")
            cc3.write("Subtotal: " + str(total_expenses) + " " + euro_symbol)
            impuesto = cc3.number_input("Impuesto %: ", min_value=0)
            if impuesto:
                imp = float("1" + '.' + str(impuesto))
                final_price = final_price * imp
            descuento = cc3.number_input("Descuento %: ", min_value=0)
            if descuento:
                final_price = final_price - ((descuento / 100) * final_price)
            cc3.write("Total: " + str(final_price) + " " + euro_symbol)

        submit = st.button("Enviar")

    # Acciones después de enviar el formulario: validaciones, mostrar resumen, generar PDF, enviar correo con adjuntos y PDF, escribir en Google Sheet
    if submit:
        if not from_who or not to_who or not num_invoice or not date_invoice or not due_date:
            st.warning("Completa los campos obligatorios")
        elif len(st.session_state.items_invoice) == 0:
            st.warning("Añade algún artículo")
        else:
            month, year = get_month_and_year()
            data = [str(from_who), str(to_who), str(logo), str(num_invoice), str(date_invoice), str(due_date), str(st.session_state.items_invoice), notes, term, str(impuesto), str(descuento), str(final_price)]
            try:
                csv_file = CSVFile(csv)
                csv_data = csv_file.read()
                csv_data.append(data)
                csv_file.write(csv_data)
                st.success("Información enviada correctamente!")
            except Exception as e:
                if 'permission denied' in str(e).lower():
                    st.warning("Tienes que cerrar el documento .csv para poder actualizar la información desde la aplicación")

            try:
                google = GoogleSheet(file_authentication_gs, google_sheet, sheet_name)
                value = [data]
                range = google.get_last_row_range()
                google.write_data(range, value)
            except Exception as excep:
                print(str(excep))
                st.warning("Hubo un problema enviando la información a Google Sheet, contacte con el administrador")
            try:
                # Generar el PDF de la factura
                api = ApiConnector()
                root_invoice=api.connect_to_api_and_save_invoice_pdf(from_who, to_who, url_logo, num_invoice, str(date_invoice), str(due_date), st.session_state.invoice_data, notes, term, impuesto, descuento)

                with open(root_invoice, 'rb') as file:
                    st.success("Factura generada correctamente!")
                    st.download_button(label="Descargar factura", data=file, file_name=f"{num_invoice}_invoice.pdf", mime="application/pdf")
                    os.remove(root_invoice)
            
            except Exception as excep:
                print(str(excep))
                st.warning("Hubo un problema generando la factura pdf.")
            
            
            try:
                # Generar el PDF de la factura
                api = ApiConnector()
                api.connect_to_api_and_save_invoice_pdf(from_who, to_who, url_logo, num_invoice, str(date_invoice), str(due_date), st.session_state.invoice_data, notes, term, impuesto, descuento)
            except Exception as excep:
                print(str(excep))
                st.warning("Hubo un problema generando la factura pdf.")

            try:
                # Enviar el correo electrónico
                if email != "":
                    send(email, f"invoices/{num_invoice}_invoice.pdf", from_who, num_invoice, to_who)
            except Exception as excep:
                print(str(excep))
                st.warning("Hubo un problema enviando el correo al destinatario especificado.")

# Si la opción seleccionada es "Visualizador de datos"
# if selected == "Visualizador de datos":
#     dataframe = pd.read_csv("invoices.csv")