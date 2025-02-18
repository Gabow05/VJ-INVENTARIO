import streamlit as st
import pandas as pd
from utils.data_manager import load_data

st.set_page_config(page_title="Inventario", page_icon="📦")

def style_dataframe(df):
    """Aplica estilos condicionales al DataFrame"""
    def highlight_low_stock(val):
        return 'background-color: #ffcdd2; color: #c62828' if val == 0 else ''

    return df.style.applymap(highlight_low_stock, subset=['cantidad'])

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

    # Filter data
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df['producto'].str.contains(search, case=False, na=False)]

    # Display inventory table with styling
    st.dataframe(
        style_dataframe(filtered_df),
        use_container_width=True,
        hide_index=True,
        column_config={
            "producto": st.column_config.TextColumn(
                "Producto",
                width="large"
            ),
            "referencia": "Referencia",
            "cantidad": st.column_config.NumberColumn(
                "Cantidad",
                help="Productos con cantidad 0 se muestran en rojo"
            ),
            "precio": st.column_config.NumberColumn(
                "Precio",
                format="$%.2f"
            ),
            "codigo": "Código"
        }
    )

    # Summary metrics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Productos", len(filtered_df))
    with col2:
        st.metric("Valor Total", f"${filtered_df['precio'].sum():,.2f}")
    with col3:
        productos_agotados = len(filtered_df[filtered_df['cantidad'] == 0])
        st.metric("Productos Agotados", productos_agotados, 
                 delta_color="inverse")

if __name__ == "__main__":
    main()