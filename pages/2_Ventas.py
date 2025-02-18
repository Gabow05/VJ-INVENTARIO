import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_manager import load_data
from utils.analysis import calculate_sales_metrics

st.set_page_config(page_title="Análisis de Ventas", page_icon="📈")

def main():
    st.title("📈 Análisis de Ventas")
    
    df = load_data()
    if df is None:
        st.warning("No hay datos disponibles para análisis.")
        return
    
    # Time period selector
    periodo = st.selectbox(
        "Seleccione período de análisis",
        ["Último mes", "Últimos 3 meses", "Último año", "Todo"]
    )
    
    # Calculate metrics
    metricas = calculate_sales_metrics(df)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ventas Totales", f"${metricas['total_ventas']:,.2f}")
    with col2:
        st.metric("Productos Vendidos", metricas['productos_vendidos'])
    with col3:
        st.metric("Ticket Promedio", f"${metricas['ticket_promedio']:,.2f}")
    
    # Charts
    st.subheader("Ventas por Categoría")
    fig = px.pie(df, values='precio', names='categoria', title='Distribución de Ventas')
    st.plotly_chart(fig)
    
    st.subheader("Tendencia de Ventas")
    # Example trend chart
    fig = px.line(df, x='fecha', y='precio', title='Tendencia de Ventas por Día')
    st.plotly_chart(fig)
    
    # Top products table
    st.subheader("Productos Más Vendidos")
    top_products = df.groupby('producto')['cantidad'].sum().sort_values(ascending=False).head(5)
    st.table(top_products)

if __name__ == "__main__":
    main()
