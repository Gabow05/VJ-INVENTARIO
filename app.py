import streamlit as st
import pandas as pd
from utils.data_manager import load_data
import os

st.set_page_config(
    page_title="Sistema de Inventario y POS",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Cargar y mostrar el logo
logo_path = "assets/logo.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=200)
else:
    st.sidebar.title("Variedades Juancho La Octava")

def main():
    st.title("🏪 Sistema de Inventario y POS")

    # Sidebar with company info
    with st.sidebar:
        st.header("Información")
        st.info("""
        Sistema de gestión de inventario y punto de venta.

        Funcionalidades:
        - Control de inventario
        - Análisis de ventas
        - Gestión de datos
        """)

        st.markdown("---")
        st.markdown("### Guía rápida")
        st.markdown("""
        1. Navegue usando el menú superior
        2. Suba sus archivos en Configuración
        3. Visualice y analice datos en las secciones correspondientes
        """)

    # Main page content
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Resumen de Inventario")
        try:
            df = load_data()
            if df is not None:
                st.metric("Total de Productos", len(df))
                st.metric("Valor del Inventario", f"${df['precio'].sum():,.2f}")
        except Exception as e:
            st.error("Error al cargar datos del inventario")

    with col2:
        st.subheader("🎯 Accesos Rápidos")
        st.button("Ver Inventario", type="primary", key="ver_inventario")
        st.button("Analizar Ventas", type="secondary", key="analizar_ventas")
        st.button("Configurar Sistema", key="configurar")

if __name__ == "__main__":
    main()