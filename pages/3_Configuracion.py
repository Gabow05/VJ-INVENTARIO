import streamlit as st
import pandas as pd
import os
from utils.data_manager import initialize_database, import_csv_to_db, load_data

st.set_page_config(page_title="Configuración", page_icon="⚙️")

def validate_csv(df):
    required_columns = ['producto', 'categoria', 'cantidad', 'precio', 'codigo']
    return all(col in df.columns for col in required_columns)

def main():
    st.title("⚙️ Configuración del Sistema")

    # Initialize database if needed
    try:
        initialize_database()
        st.success("✅ Base de datos inicializada correctamente")
    except Exception as e:
        st.error(f"❌ Error al inicializar la base de datos: {str(e)}")
        return

    st.header("Gestión de Datos")

    # File upload section
    st.subheader("Importar Datos de Inventario")
    uploaded_file = st.file_uploader(
        "Seleccione archivo CSV",
        type=['csv'],
        help="El archivo debe incluir las columnas: producto, categoria, cantidad, precio, codigo"
    )

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if validate_csv(df):
                if import_csv_to_db(uploaded_file):
                    st.success("✅ Datos importados exitosamente a la base de datos")
                    st.dataframe(df.head())
                else:
                    st.error("❌ Error al importar datos a la base de datos")
            else:
                st.error("❌ El archivo no tiene el formato correcto")
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {str(e)}")

    # System settings
    st.header("Configuración General")

    # Company information
    with st.form("company_info"):
        st.subheader("Información de la Empresa")
        company_name = st.text_input("Nombre de la Empresa")
        currency = st.selectbox("Moneda", ["USD", "MXN", "EUR"])
        tax_rate = st.number_input("Tasa de Impuesto (%)", min_value=0.0, max_value=100.0, value=16.0)

        if st.form_submit_button("Guardar Configuración"):
            st.success("✅ Configuración guardada exitosamente")

    # Data backup
    st.header("Respaldo de Datos")
    if st.button("Descargar Backup"):
        try:
            df = load_data()
            if df is not None:
                st.download_button(
                    label="📥 Descargar CSV",
                    data=df.to_csv(index=False),
                    file_name="inventory_backup.csv",
                    mime="text/csv"
                )
            else:
                st.error("No hay datos para respaldar")
        except Exception as e:
            st.error(f"Error al generar backup: {str(e)}")

if __name__ == "__main__":
    main()