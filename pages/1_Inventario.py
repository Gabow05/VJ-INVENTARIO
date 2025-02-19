import streamlit as st
import pandas as pd
from utils.data_manager import load_data

st.set_page_config(page_title="Inventario", page_icon="📦", layout="wide")

def main():
    st.title("📦 Gestión de Inventario")

    # Load data
    df = load_data()
    try:
        if df is None or df.empty:
            st.info("📝 No hay datos de inventario disponibles. Por favor, importe datos en la sección de Configuración.")
            return
    except Exception as e:
        st.error("Error al cargar datos. Por favor, intente nuevamente.")
        return

    # Búsqueda y filtros
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search = st.text_input("🔍 Buscar por nombre o código", "")
    with col2:
        precio_min = st.number_input("Precio mínimo", 0.0, value=0.0, step=1000.0)
    with col3:
        precio_max = st.number_input("Precio máximo", 0.0, value=float(df['precio'].max()), step=1000.0)
    
    hide_zero_negative = st.checkbox("Ocultar productos con cantidad 0 o negativa", value=False)

    # Aplicar filtros
    mask = pd.Series(True, index=df.index)
    
    if hide_zero_negative:
        mask = mask & (df['cantidad'] > 0)

    if search:
        search_mask = df.apply(lambda row: any(
            str(search).lower() in str(value).lower() 
            for value in row.values
        ), axis=1)
        mask = mask & search_mask

    mask = mask & (df['precio'] >= precio_min) & (df['precio'] <= precio_max)

    filtered_df = df[mask]

    # Mostrar métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Productos", len(filtered_df))
    with col2:
        valor_total = (filtered_df['precio'] * filtered_df['cantidad']).sum()
        st.metric("Valor Total", f"${valor_total:,.2f}")
    with col3:
        agotados = len(filtered_df[filtered_df['cantidad'] == 0])
        negativos = len(filtered_df[filtered_df['cantidad'] < 0])
        st.metric(f"Productos Agotados/Negativos", f"{agotados}/{negativos}")
    with col4:
        st.metric("Precio Promedio", f"${filtered_df['precio'].mean():,.2f}")

    # Mostrar tabla de inventario
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "producto": st.column_config.TextColumn(
                "Producto",
                width="large",
            ),
            "referencia": st.column_config.TextColumn(
                "Referencia",
                width="medium",
            ),
            "codigo": st.column_config.TextColumn(
                "Código",
                width="medium",
            ),
            "cantidad": st.column_config.NumberColumn(
                "Cantidad",
                help="Productos agotados se muestran en rojo",
                format="%d",
            ),
            "precio": st.column_config.NumberColumn(
                "Precio",
                format="$%,.0f",
            ),
        }
    )

    # Mostrar estadísticas adicionales
    st.markdown("### 📊 Resumen de Inventario")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Top 5 Productos más caros")
        top_expensive = filtered_df.nlargest(5, 'precio')[['producto', 'precio']]
        st.dataframe(top_expensive, hide_index=True)

    with col2:
        st.markdown("#### Productos con stock bajo (menos de 5 unidades)")
        low_stock = filtered_df[filtered_df['cantidad'] < 5][['producto', 'cantidad']]
        st.dataframe(low_stock, hide_index=True)

if __name__ == "__main__":
    main()