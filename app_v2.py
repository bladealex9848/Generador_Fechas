import streamlit as st
import pandas as pd
from datetime import datetime
import openpyxl
from io import BytesIO

# Configuración de la página de Streamlit
st.set_page_config(page_title="Generador de Turnos", page_icon="📅",
                   initial_sidebar_state='collapsed',
                   menu_items={
                       'Get Help': 'https://alexander.oviedo.isabellaea.com/',
                       'About': "Esta aplicación facilita la generación de turnos, tomando en cuenta días festivos y fines de semana."
                   })

# Título y descripción de la aplicación
st.title('Generador de Turnos')
st.write("""
Bienvenido al Generador de Turnos. Esta herramienta te permite crear una programación de turnos basada en fechas seleccionadas,
teniendo en cuenta días festivos y fines de semana. Simplemente carga los archivos necesarios y selecciona el rango de fechas.
""")

# Función para cargar y procesar los días festivos
def load_holidays(file):
    try:
        holidays_df = pd.read_csv(file, parse_dates=['fecha'])
        holidays_df['fecha'] = pd.to_datetime(holidays_df['fecha'])
        return holidays_df['fecha'].dt.date.tolist()
    except Exception as e:
        st.error(f'Ocurrió un error al procesar el archivo de festivos: {e}')
        return []


# Función para generar el rango de fechas
def generate_date_range(start_date, end_date, num_entries, orientation, days_option, include_holidays, holidays):
    dates = pd.date_range(start_date, end_date)
    
    if days_option == 'Días de Semana':
        dates = dates[dates.dayofweek < 5]  # Lunes a Viernes
    elif days_option == 'Fines de Semana':
        dates = dates[dates.dayofweek >= 5]  # Sábado y Domingo

    # Convertir las fechas de los días festivos a datetime para comparación
    if include_holidays and holidays:
        holidays = pd.to_datetime(holidays)

    # Incluir los festivos si la opción está seleccionada
    if include_holidays:
        # Unir los festivos con los fines de semana
        dates = dates.union(holidays)

    # Eliminar duplicados en caso de que un festivo también sea un fin de semana
    dates = dates.drop_duplicates()

    # Filtrar las fechas para que coincidan con la opción seleccionada después de unir con los festivos
    if days_option == 'Fines de Semana':
        dates = dates[dates.dayofweek >= 5]  # Asegurarse de que solo quedan los fines de semana y festivos
    elif days_option == 'Días de Semana':
        dates = dates[dates.dayofweek < 5]  # Asegurarse de que solo quedan los días de semana

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
            df[i // num_entries] = date_strings[i:i + num_entries] + [''] * (num_entries - len(date_strings[i:i + num_entries]))

    return df

# Widget de carga de archivo
uploaded_file = st.file_uploader("Carga un archivo de festivos (formato CSV)", type='csv')
holidays = load_holidays(uploaded_file) if uploaded_file is not None else []

# Widget para seleccionar las fechas a incluir
days_option = st.selectbox('Selecciona las fechas a incluir', ['Todos los días', 'Días de Semana', 'Fines de Semana'])

# Checkbox para incluir o no los días festivos
include_holidays = st.checkbox('Incluir festivos', value=False) if holidays else False

# Widgets para seleccionar el rango de fechas y el número de entradas
start_date = st.date_input('Fecha de inicio', datetime.today())
end_date = st.date_input('Fecha final', datetime.today())
num_entries = st.number_input('Número de filas/columnas', min_value=1, value=1)

# Radio buttons para la orientación
orientation = st.radio("Selecciona la orientación para la distribución de las fechas", ('Horizontal', 'Vertical'))

# Botón para generar el Excel
if st.button('Generar Excel'):
    if start_date <= end_date:
        df = generate_date_range(start_date, end_date, num_entries, orientation, days_option, include_holidays, holidays)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        
        st.success('¡El archivo Excel se ha generado con éxito!')
        st.download_button(label='Descargar Excel', data=output.getvalue(),
                           file_name='Fechas.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        st.error('La fecha de inicio debe ser anterior a la fecha final.')

# Pie de página con información del creador
st.sidebar.markdown('---')
st.sidebar.subheader('Creado por:')
st.sidebar.markdown('Alexander Oviedo Fadul')
st.sidebar.markdown("[GitHub](https://github.com/bladealex9848) | [Website](https://alexander.oviedo.isabellaea.com/) | [Instagram](https://www.instagram.com/alexander.oviedo.fadul) | [Twitter](https://twitter.com/alexanderofadul) | [Facebook](https://www.facebook.com/alexanderof/) | [WhatsApp](https://api.whatsapp.com/send?phone=573015930519&text=Hola%20!Quiero%20conversar%20contigo!%20)")