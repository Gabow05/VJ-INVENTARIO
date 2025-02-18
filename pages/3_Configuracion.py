import streamlit as st
import pandas as pd
import os
from utils.data_manager import initialize_database, import_file_to_db, load_data

st.set_page_config(page_title="Configuración", page_icon="⚙️")

def validate_file(file):
    file_extension = os.path.splitext(file.name)[1].lower()
    return file_extension in ['.csv', '.xlsx', '.xls']

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
    st.markdown("""
    ### Formato del archivo
    El archivo debe contener las siguientes columnas:
    - nombre o producto
    - refer o referencia
    - codigo
    - q_fin o cantidad
    - pvta1i o precio
    
    Se aceptan archivos en formato:
    - CSV (separado por comas o punto y coma)
    - Excel (.xls, .xlsx)
    """)
    
    uploaded_file = st.file_uploader(
        "Seleccione archivo (CSV o Excel)",
        type=['csv', 'xlsx', 'xls'],
        help="Se intentarán detectar automáticamente las columnas y el formato", codigo"
    )

    if uploaded_file is not None:
        try:
            if validate_file(uploaded_file):
                if import_file_to_db(uploaded_file):
                    st.success("✅ Datos importados exitosamente")
                    # Mostrar vista previa de los datos importados
                    df = load_data()
                    if df is not None:
                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "cantidad": st.column_config.NumberColumn(
                                    "Cantidad",
                                    help="Productos con cantidad 0 se muestran en rojo"
                                ),
                                "precio": st.column_config.NumberColumn(
                                    "Precio",
                                    format="$%.2f"
                                )
                            }
                        )
                else:
                    st.error("❌ Error al importar datos")
            else:
                st.error("❌ Formato de archivo no soportado")
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {str(e)}")

    # System settings
    st.header("Configuración General")

    # Company information
    with st.form("company_info"):
        st.subheader("Información de la Empresa")
        company_name = st.text_input("Nombre de la Empresa", "Variedades Juancho La Octava")
        currency = st.selectbox("Moneda", ["COP", "USD", "EUR"])
        tax_rate = st.number_input("Tasa de Impuesto (%)", min_value=0.0, max_value=100.0, value=19.0)

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