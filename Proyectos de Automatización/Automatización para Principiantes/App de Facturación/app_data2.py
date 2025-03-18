import streamlit as st
import pandas as pd
import uuid
import re
import os
import requests
from datetime import datetime
from streamlit_option_menu import option_menu
import base64
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Carga variables de entorno
load_dotenv()

# ------------ CONFIGURACIONES --------------
page_title = "Generador de facturas"
page_icon = "📊"
layout = "wide"
peso_symbol = "$"  # Símbolo de pesos argentinos
csv_file_path = "invoices.csv"


# Configuración de la página de Streamlit
st.set_page_config(
    page_title=page_title,
    page_icon=page_icon,
    layout=layout,
    initial_sidebar_state="expanded"
)

if "theme" not in st.session_state:
    st.session_state.theme = "light"  # Valor predeterminado

# Función para configurar el modo oscuro/claro
def set_theme():
    
    # Estilos CSS para tema oscuro/claro
    if st.session_state.theme == "dark":
        theme_css = """
        <style>
        .main {background-color: #0E1117; color: #FAFAFA;}
        .stButton>button {background-color: #4B0082; color: white;}
        .stTextInput>div>div>input {background-color: #262730; color: white;}
        .stTextArea>div>div>textarea {background-color: #262730; color: white;}
        .stNumberInput>div>div>input {background-color: #262730; color: white;}
        .stDataFrame {color: white;}
        .css-zt5igj {border-left-color: #4B0082 !important;}
        div[data-testid="stSidebar"] {background-color: #111621;}
        </style>
        """
    else:
        theme_css = """
        <style>
        .main {background-color: #FFFFFF; color: #31333F;}
        .stButton>button {background-color: #4169E1; color: white;}
        .stTextInput>div>div>input {background-color: #F0F2F6; color: black;}
        .stTextArea>div>div>textarea {background-color: #F0F2F6; color: black;}
        .stNumberInput>div>div>input {background-color: #F0F2F6; color: black;}
        .css-zt5igj {border-left-color: #4169E1 !important;}
        </style>
        """
    
    st.markdown(theme_css, unsafe_allow_html=True)

# Ocultar elementos de Streamlit y aplicar tema
def apply_styles():
    hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
    st.markdown(hide_st_style, unsafe_allow_html=True)
    set_theme()

# Aplicar estilos
apply_styles()

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

# Función para validar CUIT/CUIL argentino
def validate_cuit(cuit):
    # Eliminar guiones y espacios
    cuit = re.sub(r'[-\s]', '', cuit)
    
    # Verificar que tenga 11 dígitos
    if not re.match(r'^\d{11}$', cuit):
        return False
    
    # Algoritmo de validación de CUIT/CUIL argentino
    base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    aux = 0
    for i in range(10):
        aux += int(cuit[i]) * base[i]
    
    aux = 11 - (aux % 11)
    if aux == 11:
        aux = 0
    elif aux == 10:
        aux = 9
    
    return aux == int(cuit[10])

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
                f.write("from_who,to_who,cuit_emisor,cuit_receptor,logo,num_invoice,date_invoice,due_date,items,notes,term,impuesto,descuento,tipo_factura,final_price\n")
            return []
        else:
            return pd.read_csv(file_path).values.tolist()
    except Exception as e:
        st.error(f"Error al leer el CSV: {str(e)}")
        return []

# Función para escribir en el CSV
def write_csv(file_path, data):
    try:
        df = pd.DataFrame(data, columns=["from_who", "to_who", "cuit_emisor", "cuit_receptor", "logo", "num_invoice", "date_invoice", "due_date", "items", "notes", "term", "impuesto", "descuento", "tipo_factura", "final_price"])
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        st.error(f"Error al escribir en el CSV: {str(e)}")
        return False

# Función para generar el PDF de la factura
def generate_invoice_pdf(from_who, to_who, cuit_emisor, cuit_receptor, logo, number, date, due_date, items, notes, terms, tax, discounts, tipo_factura):
    invoices_directory = "invoices"
    if not os.path.exists(invoices_directory):
        os.makedirs(invoices_directory)
        
    # Incluir la API key en los headers
    api_key = os.getenv("INVOICE_API_KEY", "sk_H6UjYgzPrePSC4Aozptr9CuEtLx9lPxA")  # Usar variable de entorno o el valor predeterminado
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    url = 'https://invoice-generator.com'
    
    # Agregar información fiscal de Argentina
    footer_text = f"""
    {tipo_factura}
    CUIT Emisor: {cuit_emisor}
    CUIT Receptor: {cuit_receptor}
    Esta factura es válida como comprobante fiscal según normativa AFIP.
    """
    
    # Enriquecer notas con información fiscal
    full_notes = f"{notes}\n\n{footer_text}" if notes else footer_text
    
    invoice_parsed = {
        'from': from_who,
        'to': to_who,
        'logo': logo,
        'number': number,
        'currency': 'ARS',  # Usando ARS para pesos argentinos
        'date': date,
        'due_date': due_date,
        'items': items,
        'fields': {"tax": "%", "discounts": "%", "shipping": False},
        'discounts': discounts,
        'tax': tax,
        'notes': full_notes,
        'terms': terms
    }
    
    try:
        r = requests.post(url, json=invoice_parsed, headers=headers)
        if r.status_code == 200 or r.status_code == 201:
            pdf = r.content
            invoice_path = f"{invoices_directory}/{number}_factura.pdf"
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

# Función para crear el footer personalizado
def custom_footer():
    footer = """
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background-color: #f0f2f6; padding: 10px; text-align: center; color: #31333F;">
        <p>© 2025 Federico Martinez - Todos los derechos reservados | 
        <a href="https://fede-martinez-portfolio.vercel.app/" target="_blank" style="color: #4169E1;">Portfolio</a> | 
        <a href="https://www.linkedin.com/in/federicoluismartinez/" target="_blank" style="color: #4169E1;">LinkedIn</a></p>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)

# --------------- Código del frontend ------------------

# --- BARRA LATERAL PARA CONFIGURACIONES ---
with st.sidebar:
    
    st.write("---")
    st.write("💼 Configuración de Facturación")
    
    # Definir tipos de factura relevantes para Argentina
    tipo_factura = st.selectbox(
        "Tipo de Factura",
        ["Factura A", "Factura B", "Factura C", "Factura E", "Nota de Crédito", "Nota de Débito"]
    )
    
    # Información sobre cada tipo de factura
    if tipo_factura == "Factura A":
        st.info("📝 Para contribuyentes inscriptos en el IVA.")
    elif tipo_factura == "Factura B":
        st.info("📝 Para consumidores finales o monotributistas.")
    elif tipo_factura == "Factura C":
        st.info("📝 Emitida por monotributistas.")
    elif tipo_factura == "Factura E":
        st.info("📝 Para exportaciones.")
    elif "Nota" in tipo_factura:
        st.info("📝 Para ajustes sobre facturas emitidas.")

# --- MENÚ DE NAVEGACIÓN ---
selected = option_menu(
    menu_title=None,
    options=["📄 Facturación", "📊 Visualizador de datos"],
    icons=["receipt", "bar-chart-fill"],
    orientation="horizontal",
)

# Si la opción seleccionada es "Facturación"
if selected == "📄 Facturación":
    st.title("🧾 Generador de Facturas")
    st.caption("Crea facturas electrónicas para tu negocio en Argentina")
    
    # Sección de información de la factura
    with st.container():
        cc1, cc2 = st.columns(2)
        
        # Columna izquierda: información del emisor
        from_who = cc1.text_input("📤 Emisor: ", placeholder="Nombre o razón social")
        cuit_emisor = cc1.text_input("🔢 CUIT Emisor: ", placeholder="XX-XXXXXXXX-X")
        if cuit_emisor and not validate_cuit(cuit_emisor):
            cc1.warning("El CUIT del emisor no es válido")
        
        # Columna izquierda: información del receptor
        to_who = cc1.text_input("📥 Cliente: ", placeholder="Nombre o razón social del cliente")
        cuit_receptor = cc1.text_input("🔢 CUIT/CUIL Receptor: ", placeholder="XX-XXXXXXXX-X")
        if cuit_receptor and not validate_cuit(cuit_receptor):
            cc1.warning("El CUIT/CUIL del receptor no es válido")
        
        # Email para envío
        email = cc1.text_input("📧 Enviar a: ", placeholder="Correo electrónico (opcional)")
        if email:
            validation = validate_email(email)
            if validation == False:
                cc1.warning("El correo electrónico no tiene un formato válido.")
            else:
                cc1.success("La factura generada será enviada a este destinatario.")
        
        # Columna derecha: detalles de la factura
        cc2.subheader(f"{tipo_factura} 📃")
        
        num_invoice = cc2.text_input("#", placeholder="00001-00000001")
        if num_invoice and not re.match(r'^\d{5}-\d{8}$', num_invoice):
            cc2.warning("El formato del número de factura debe ser: 00001-00000001")
        
        # Fechas de la factura
        date_invoice = cc2.date_input("📅 Fecha de emisión")
        due_date = cc2.date_input("⏱️ Fecha de vencimiento")
        payment_terms = cc2.text_input("💰 Condiciones de pago", placeholder="Ej: Pago en 30 días")

    # Formulario para los gastos
    with st.form("entry_form", clear_on_submit=True):
        st.subheader("Detalle de productos/servicios")
        cex1, cex2, cex3 = st.columns(3)
        articulo = cex1.text_input("📦 Artículo", placeholder="Descripción del servicio o producto")
        amount_expense = cex2.number_input("🔢 Cantidad", step=1, min_value=1)
        precio = cex3.number_input("💲 Precio unitario (ARS)", min_value=0)
        submitted_expense = st.form_submit_button("Añadir artículo")
        if submitted_expense:
            if articulo == "":
                st.warning("⚠️ Añade una descripción del artículo o servicio")
            else:
                st.success("✅ Artículo añadido")
                st.session_state.expense_data.append({"Artículo": articulo, "Cantidad": amount_expense, "Precio unitario": precio, "Total": amount_expense * precio})
                st.session_state.invoice_data.append({"name": articulo, "quantity": amount_expense, "unit_cost": precio})

    # Mostrar la tabla de artículos añadidos
    total_expenses = 0
    final_price = 0
    if st.session_state.expense_data:
        df_expense = pd.DataFrame(st.session_state.expense_data)
        df_expense_invoice = pd.DataFrame(st.session_state.invoice_data)
        st.subheader("📋 Artículos añadidos")
        st.table(df_expense)
        total_expenses = df_expense["Total"].sum()
        st.text(f"Subtotal: {peso_symbol} {total_expenses:,.2f}")
        final_price = total_expenses

    # Sección de información adicional de la factura
    with st.container():
        cc3, cc4 = st.columns(2)
        notes = cc3.text_area("📝 Notas", placeholder="Información adicional para el cliente")
        term = cc4.text_area("📜 Términos", placeholder="Términos y condiciones de la factura")
        
        # Cálculos fiscales para Argentina
        cc3.write(f"Subtotal: {peso_symbol} {total_expenses:,.2f}")
        
        # IVA y otros impuestos argentinos
        impuesto_options = cc3.selectbox(
            "Tipo de impuesto", 
            ["IVA 21%", "IVA 10.5%", "IVA 27%", "Exento", "Personalizado"]
        )
        
        if impuesto_options == "IVA 21%":
            impuesto = 21
        elif impuesto_options == "IVA 10.5%":
            impuesto = 10.5
        elif impuesto_options == "IVA 27%":
            impuesto = 27
        elif impuesto_options == "Exento":
            impuesto = 0
        else:
            impuesto = cc3.number_input("Impuesto %: ", min_value=0.0)
        
        # Mostrar cálculo de impuestos
        if impuesto > 0:
            imp_amount = total_expenses * (impuesto / 100)
            cc3.write(f"+ {impuesto_options}: {peso_symbol} {imp_amount:,.2f}")
            final_price = total_expenses + imp_amount
        
        # Percepciones e impuestos adicionales
        perc_options = cc3.multiselect(
            "Percepciones adicionales",
            ["IIBB (3%)", "IVA Percepción (5%)", "Impuesto al Cheque (1.2%)", "Percepción Municipal (1%)"]
        )
        
        percepciones_total = 0
        if perc_options:
            for perc in perc_options:
                if "IIBB" in perc:
                    perc_rate = 3
                elif "IVA Percepción" in perc:
                    perc_rate = 5
                elif "Cheque" in perc:
                    perc_rate = 1.2
                elif "Municipal" in perc:
                    perc_rate = 1
                else:
                    perc_rate = 0
                
                perc_amount = total_expenses * (perc_rate / 100)
                percepciones_total += perc_amount
                cc3.write(f"+ {perc}: {peso_symbol} {perc_amount:,.2f}")
            
            final_price += percepciones_total
        
        # Descuentos
        descuento = cc3.number_input("Descuento %: ", min_value=0.0)
        if descuento > 0:
            desc_amount = final_price * (descuento / 100)
            cc3.write(f"- Descuento ({descuento}%): {peso_symbol} {desc_amount:,.2f}")
            final_price -= desc_amount
        
        # Total final
        cc3.markdown(f"### Total: {peso_symbol} {final_price:,.2f}")
        
        # Información de pago
        cc4.subheader("💳 Información de pago")
        payment_method = cc4.selectbox(
            "Método de pago",
            ["Transferencia bancaria", "Efectivo", "Mercado Pago", "Tarjeta de crédito", "Cheque"]
        )
        
        if payment_method == "Transferencia bancaria":
            payment_info = cc4.text_area("Datos bancarios", placeholder="CBU/Alias, Banco, Titular de la cuenta", height=100)
        elif payment_method == "Mercado Pago":
            payment_info = cc4.text_input("Enlace o CVU de Mercado Pago")
        else:
            payment_info = cc4.text_area("Detalles del pago", height=100)

    submit = st.button("🧾 Generar Factura")

    # Acciones después de enviar el formulario
    if submit:
        if not from_who or not to_who or not num_invoice or not date_invoice or not due_date:
            st.warning("⚠️ Completa los campos obligatorios")
        elif not cuit_emisor or not cuit_receptor or not validate_cuit(cuit_emisor) or not validate_cuit(cuit_receptor):
            st.warning("⚠️ Los CUIT/CUIL ingresados no son válidos")
        elif len(st.session_state.expense_data) == 0:
            st.warning("⚠️ Añade algún artículo")
        else:
            month, year = get_month_and_year()
            
            # Preparar información de pago para incluir en notas
            payment_notes = f"\n\nMétodo de pago: {payment_method}"
            if payment_info:
                payment_notes += f"\n{payment_info}"
            
            full_notes = notes + payment_notes
            
            # 1. Guardar en CSV
            existing_data = read_csv(csv_file_path)
            new_row = [from_who, to_who, cuit_emisor, cuit_receptor, num_invoice, str(date_invoice), str(due_date), 
                      str(st.session_state.invoice_data), full_notes, term, str(impuesto), str(descuento), tipo_factura, str(final_price)]
            
            if existing_data:
                existing_data.append(new_row)
            else:
                existing_data = [new_row]
                
            if write_csv(csv_file_path, existing_data):
                st.success("✅ Información guardada en CSV correctamente!")
            
            # 2. Generar PDF
            invoice_path = generate_invoice_pdf(
                from_who, to_who, cuit_emisor, cuit_receptor,"MateSpark Analytics LLC", num_invoice, str(date_invoice), str(due_date), 
                st.session_state.invoice_data, full_notes, term, impuesto, descuento, tipo_factura
            )
            
            if invoice_path:
                with open(invoice_path, 'rb') as file:
                    st.success("✅ Factura generada correctamente!")
                    st.download_button(
                        label="⬇️ Descargar factura", 
                        data=file, 
                        file_name=f"{num_invoice}_factura.pdf", 
                        mime="application/pdf"
                    )
                
                # 3. Enviar por email si hay dirección
                if email and validate_email(email):
                    if send_email(email, invoice_path, from_who, num_invoice, to_who):
                        st.success(f"✅ Se ha enviado la factura a {email}")

# Si la opción seleccionada es "Visualizador de datos"
elif selected == "📊 Visualizador de datos":
    st.title("📊 Visualizador de datos")
    
    try:
        if os.path.exists(csv_file_path):
            df = pd.read_csv(csv_file_path)
            if not df.empty:
                st.subheader("📋 Facturas registradas")
                st.dataframe(df)
                
                # Análisis básico
                st.subheader("📈 Resumen")
                total_facturas = len(df)
                total_ingresos = df['final_price'].astype(float).sum() if 'final_price' in df.columns else 0
                
                # Dashboard con métricas
                col1, col2, col3 = st.columns(3)
                col1.metric("📊 Total de facturas", total_facturas)
                col2.metric("💰 Total de ingresos", f"{peso_symbol} {total_ingresos:,.2f}")
                
                # Si hay suficientes datos, calcular promedio
                if total_facturas > 0:
                    promedio = total_ingresos / total_facturas
                    col3.metric("📏 Promedio por factura", f"{peso_symbol} {promedio:,.2f}")
                
                # Análisis por tipo de factura
                if 'tipo_factura' in df.columns:
                    st.subheader("📊 Análisis por tipo de factura")
                    tipo_counts = df['tipo_factura'].value_counts()
                    st.bar_chart(tipo_counts)
                    
                    # Análisis de ingresos por tipo de factura
                    ingresos_por_tipo = df.groupby('tipo_factura')['final_price'].sum().astype(float)
                    st.subheader("💰 Ingresos por tipo de factura")
                    st.bar_chart(ingresos_por_tipo)
                
                # Exportar datos
                st.download_button(
                    label="⬇️ Exportar datos como CSV",
                    data=df.to_csv().encode('utf-8'),
                    file_name='analisis_facturas.csv',
                    mime='text/csv',
                )
            else:
                st.info("ℹ️ No hay datos de facturas registrados todavía.")
        else:
            st.info("ℹ️ No se encontró el archivo CSV. Crea facturas primero.")
    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {str(e)}")

# Agregar el footer personalizado
custom_footer()