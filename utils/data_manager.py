import pandas as pd
import os
from .models import get_db, Producto, Venta, init_db
from datetime import datetime

def initialize_database():
    """Initialize database and create tables"""
    init_db()

def load_data():
    """
    Load inventory data from database
    """
    try:
        db = get_db()
        productos = db.query(Producto).all()
        data = [{
            'producto': p.nombre,
            'categoria': p.categoria,
            'cantidad': p.cantidad,
            'precio': p.precio,
            'codigo': p.codigo,
            'fecha': p.fecha_actualizacion
        } for p in productos]
        return pd.DataFrame(data) if data else pd.DataFrame(columns=['producto', 'categoria', 'cantidad', 'precio', 'codigo', 'fecha'])
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
    finally:
        if 'db' in locals():
            db.close()

def save_data(df):
    """
    Save inventory data to database
    """
    db = None
    try:
        db = get_db()
        # Clear existing products
        db.query(Producto).delete()

        # Add new products
        for _, row in df.iterrows():
            producto = Producto(
                nombre=row['producto'],
                categoria=row['categoria'],
                cantidad=row['cantidad'],
                precio=row['precio'],
                codigo=row['codigo'],
                fecha_actualizacion=datetime.now()
            )
            db.add(producto)

        db.commit()
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        if db:
            db.rollback()
        return False
    finally:
        if db:
            db.close()

def import_csv_to_db(file_path):
    """
    Import data from CSV file to database
    """
    try:
        df = pd.read_csv(file_path)
        df = df.rename(columns={
            'producto': 'producto',
            'categoria': 'categoria',
            'cantidad': 'cantidad',
            'precio': 'precio',
            'codigo': 'codigo'
        })
        return save_data(df)
    except Exception as e:
        print(f"Error importing CSV: {e}")
        return False