import pandas as pd
import numpy as np

def calculate_sales_metrics(df):
    """
    Calculate basic sales metrics from DataFrame
    """
    metrics = {
        'total_ventas': df['precio'].sum(),
        'productos_vendidos': df['cantidad'].sum(),
        'ticket_promedio': df['precio'].mean(),
        'categorias': len(df['categoria'].unique())
    }
    return metrics

def analyze_trends(df):
    """
    Analyze sales trends
    """
    trends = {
        'daily_sales': df.groupby('fecha')['precio'].sum(),
        'category_sales': df.groupby('categoria')['precio'].sum(),
        'top_products': df.groupby('producto')['cantidad'].sum().sort_values(ascending=False).head(10)
    }
    return trends
