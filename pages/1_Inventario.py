import streamlit as st
import pandas as pd
from utils.data_manager import load_data

st.set_page_config(page_title="Inventario", page_icon="📦")

def main():
    st.title("📦 Gestión de Inventario")
    
    # Load data
    df = load_data()
    
    if df is None:
        st.warning("No hay datos de inventario disponibles. Por favor, suba un archivo CSV en la sección de Configuración.")
        return
    
    # Search and filters
    col1, col2 = st.columns([2,1])
    with col1:
        search = st.text_input("🔍 Buscar producto", "")
    with col2:
        category = st.selectbox("Categoría", ["Todas"] + list(df['categoria'].unique()))
    
    # Filter data
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df['producto'].str.contains(search, case=False)]
    if category != "Todas":
        filtered_df = filtered_df[filtered_df['categoria'] == category]
    
    # Display inventory table
    st.dataframe(
        filtered_df,
        column_config={
            "producto": "Producto",
            "categoria": "Categoría",
            "cantidad": "Cantidad",
            "precio": st.column_config.NumberColumn(
                "Precio",
                format="$%.2f"
            ),
            "codigo": "Código"
        },
        hide_index=True,
    )
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Productos", len(filtered_df))
    with col2:
        st.metric("Valor Total", f"${filtered_df['precio'].sum():,.2f}")
    with col3:
        st.metric("Categorías", len(filtered_df['categoria'].unique()))

if __name__ == "__main__":
    main()
