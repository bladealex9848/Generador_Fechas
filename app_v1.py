import streamlit as st
import pandas as pd
from datetime import datetime
import openpyxl
from io import BytesIO

# Configuración de la página de Streamlit para la aplicación de Generador de Turnos
st.set_page_config(
    page_title="Generador de Turnos",
    page_icon="📅",  # Cambia el ícono según tu preferencia
    initial_sidebar_state='collapsed',
    menu_items={
        'Get Help': 'https://alexander.oviedo.isabellaea.com/',  # Enlace de ayuda, cámbialo según necesites
        'Report a bug': None,  # O un enlace para reportar errores
        'About': "Esta aplicación facilita la generación de turnos, tomando en cuenta días festivos y fines de semana."
    }
)

# Título y presentación de la aplicación
st.title('Generador de Turnos')
st.write("""
Bienvenido al Generador de Turnos. Esta aplicación te permite crear una programación de turnos basada en fechas seleccionadas, 
considerando días festivos y fines de semana. Simplemente carga los archivos necesarios y selecciona el rango de fechas.
""")

# Define una función para generar el rango de fechas
def generate_date_range(start_date, end_date, num_entries, orientation):
    # Calcula el rango de fechas
    dates = pd.date_range(start_date, end_date)
    # Convierte el rango de fechas en una lista de strings
    date_strings = [date.strftime('%d/%m/%Y') for date in dates]
    
    # Organiza las fechas según la orientación seleccionada
    if orientation == 'Horizontal':
        # Divide las fechas en el número de columnas especificado y las organiza en filas
        chunks = [date_strings[i:i + num_entries] for i in range(0, len(date_strings), num_entries)]
        df = pd.DataFrame(chunks)
    else:
        # Divide las fechas en el número de filas especificado y las organiza en columnas
        df = pd.DataFrame()
        for i in range(0, len(date_strings), num_entries):
            df[i//num_entries] = date_strings[i:i + num_entries] + [''] * (num_entries - len(date_strings[i:i + num_entries]))
    
    return df

# Crea los widgets de entrada para las fechas, el número de filas/columnas y la orientación
start_date = st.date_input('Fecha de inicio', datetime.today())
end_date = st.date_input('Fecha final', datetime.today())
num_entries = st.number_input('Número de filas/columnas', min_value=1, value=1)
orientation = st.radio("Selecciona la orientación para la distribución de las fechas", ('Horizontal', 'Vertical'))

# Botón para generar el Excel
if st.button('Generar Excel'):
    if start_date and end_date and num_entries:
        # Genera el rango de fechas
        df = generate_date_range(start_date, end_date, num_entries, orientation)
        # Convierte el DataFrame a un archivo Excel en la memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        
        # Muestra un enlace para descargar el archivo Excel
        st.success('¡El archivo Excel se ha generado con éxito!')
        st.download_button(label='Descargar Excel',
                           data=output.getvalue(),
                           file_name='Fechas.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        st.error('Por favor, rellene todas las entradas.')
        
# Footer
st.sidebar.markdown('---')
st.sidebar.subheader('Creado por:')
st.sidebar.markdown('Alexander Oviedo Fadul')
st.sidebar.markdown("[GitHub](https://github.com/bladealex9848) | [Website](https://alexander.oviedo.isabellaea.com/) | [Instagram](https://www.instagram.com/alexander.oviedo.fadul) | [Twitter](https://twitter.com/alexanderofadul) | [Facebook](https://www.facebook.com/alexanderof/) | [WhatsApp](https://api.whatsapp.com/send?phone=573015930519&text=Hola%20!Quiero%20conversar%20contigo!%20)")