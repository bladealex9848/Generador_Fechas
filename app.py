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
                       'About': """Esta aplicación permite generar un programa de turnos personalizado,
                                   considerando días laborables, fines de semana y festivos según las preferencias del usuario.
                                   Ofrece opciones para incluir o excluir festivos y para organizar las fechas generadas
                                   de forma horizontal o vertical, adaptándose a diversas necesidades de planificación."""
                   })

# Título y descripción de la aplicación
st.title('📅 Generador de Turnos')

st.write("""
    [![ver código fuente](https://img.shields.io/badge/Repositorio%20GitHub-gris?logo=github)](https://github.com/bladealex9848/Generador_Fechas)
    ![Visitantes](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgeneradorfechas.streamlit.app&label=Visitantes&labelColor=%235d5d5d&countColor=%231e7ebf&style=flat)
    """)

st.write("""
Bienvenido al Generador de Turnos. Con esta herramienta interactiva, puedes crear una programación de turnos 
adaptada a tus necesidades específicas. Carga un archivo con los días festivos, define el rango de fechas, 
elige incluir o excluir fines de semana y festivos, y selecciona la orientación de la distribución de las fechas.
La aplicación genera un archivo Excel listo para descargar, facilitando la gestión de tus recursos y la planificación del tiempo.
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
    # Convertir las fechas de inicio y fin a datetime para comparación
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Generar el rango de fechas completo
    all_dates = pd.date_range(start_date, end_date)
    
    # Filtrar los festivos para que solo estén dentro del rango de fechas
    if holidays:
        holidays = pd.to_datetime(holidays)
        holidays_in_range = holidays[(holidays >= start_date) & (holidays <= end_date)]
    else:
        holidays_in_range = pd.to_datetime([])  # Lista vacía si no hay festivos
    
    # Decidir qué fechas incluir basado en la selección de días de semana o fines de semana
    if days_option == 'Todos los días':
        if include_holidays:
            dates = all_dates.union(holidays_in_range).sort_values()
        else:
            dates = all_dates.difference(holidays_in_range).sort_values()
    elif days_option == 'Días de Semana':
        weekdays = all_dates[all_dates.dayofweek < 5]  # Lunes a Viernes
        if include_holidays:
            dates = weekdays.union(holidays_in_range).sort_values()
        else:
            dates = weekdays.difference(holidays_in_range).sort_values()
    elif days_option == 'Fines de Semana':
        weekends = all_dates[all_dates.dayofweek >= 5]  # Sábado y Domingo
        if include_holidays:
            dates = weekends.union(holidays_in_range).sort_values()
        else:
            dates = weekends.difference(holidays_in_range).sort_values()
    
    date_strings = [date.strftime('%d/%m/%Y') for date in dates]
    
    # Organiza las fechas según la orientación seleccionada
    if orientation == 'Horizontal':
        chunks = [date_strings[i:i + num_entries] for i in range(0, len(date_strings), num_entries)]
        df = pd.DataFrame(chunks)
    else:  # Vertical
        # Crea las columnas con las fechas distribuidas verticalmente
        columns = [date_strings[i:i + num_entries] for i in range(0, len(date_strings), num_entries)]
        # Rellenar las columnas para que todas tengan la misma longitud
        max_len = max(map(len, columns))
        columns_padded = [col + [''] * (max_len - len(col)) for col in columns]
        df = pd.DataFrame(columns_padded).transpose()

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
st.sidebar.markdown("[GitHub](https://github.com/bladealex9848) | [Website](https://www.alexanderoviedofadul.dev/) | [Instagram](https://www.instagram.com/alexander.oviedo.fadul) | [Twitter](https://twitter.com/alexanderofadul) | [Facebook](https://www.facebook.com/alexanderof/) | [WhatsApp](https://api.whatsapp.com/send?phone=573015930519&text=Hola%20!Quiero%20conversar%20contigo!%20)")
