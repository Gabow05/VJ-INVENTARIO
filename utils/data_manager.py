import pandas as pd
import os
from .models import get_db, Producto, Venta, init_db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

def initialize_database():
    """Initialize database and create tables"""
    return init_db()

def load_data():
    """
    Load inventory data from database
    """
    db = get_db()
    try:
        productos = db.query(Producto).all()
        data = [{
            'producto': p.nombre,
            'categoria': p.categoria,
            'cantidad': p.cantidad,
            'precio': p.precio,
            'codigo': p.codigo,
            'fecha': p.fecha_actualizacion
        } for p in productos]
        return pd.DataFrame(data) if data else pd.DataFrame(
            columns=['producto', 'categoria', 'cantidad', 'precio', 'codigo', 'fecha']
        )
    except SQLAlchemyError as e:
        print(f"Error loading data: {e}")
        return None
    finally:
        db.close()

def save_data(df):
    """
    Save inventory data to database
    """
    db = get_db()
    try:
        # Clear existing products
        db.query(Producto).delete()

        # Add new products
        for _, row in df.iterrows():
            producto = Producto(
                nombre=row['producto'],
                categoria=row['categoria'],
                cantidad=int(row['cantidad']),
                precio=float(row['precio']),
                codigo=row['codigo'],
                fecha_actualizacion=datetime.now()
            )
            db.add(producto)

        db.commit()
        return True
    except SQLAlchemyError as e:
        print(f"Error saving data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def import_csv_to_db(file_path):
    """
    Import data from CSV file to database
    """
    try:
        # Read CSV with explicit data types
        df = pd.read_csv(
            file_path,
            dtype={
                'producto': str,
                'categoria': str,
                'cantidad': int,
                'precio': float,
                'codigo': str
            }
        )

        # Validate required columns
        required_columns = ['producto', 'categoria', 'cantidad', 'precio', 'codigo']
        if not all(col in df.columns for col in required_columns):
            print("Missing required columns in CSV")
            return False

        return save_data(df)
    except Exception as e:
        print(f"Error importing CSV: {e}")
        return False