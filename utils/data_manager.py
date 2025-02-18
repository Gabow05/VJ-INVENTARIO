import pandas as pd
import os
from .models import get_db, Producto, init_db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import tempfile

def load_data():
    """
    Load inventory data from database
    """
    db = get_db()
    try:
        productos = db.query(Producto).all()
        data = []
        for p in productos:
            data.append({
                'producto': p.nombre,
                'referencia': p.referencia,
                'codigo': p.codigo,
                'cantidad': p.cantidad,
                'precio': p.precio
            })
        return pd.DataFrame(data) if data else None
    except SQLAlchemyError as e:
        print(f"Error loading data: {e}")
        return None
    finally:
        db.close()

def process_csv_data(file_path):
    """
    Process the CSV file with specific encoding and format
    """
    try:
        df = pd.read_csv(file_path, sep=';', encoding='utf-8-sig')

        # Renombrar columnas según el archivo proporcionado
        df = df.rename(columns={
            'nombre': 'producto',
            'refer': 'referencia',
            'codigo': 'codigo',
            'q_fin': 'cantidad',
            'pvta1i': 'precio'
        })

        # Seleccionar solo las columnas que necesitamos
        columns = ['producto', 'referencia', 'codigo', 'cantidad', 'precio']
        df = df[columns]

        # Limpiar y convertir datos
        df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0).astype(int)
        df['precio'] = pd.to_numeric(df['precio'], errors='coerce').fillna(0).astype(float)

        return df
    except Exception as e:
        print(f"Error processing CSV: {e}")
        return None

def import_file_to_db(uploaded_file):
    """
    Import data from CSV file to database
    """
    try:
        # Guardar archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name

        try:
            # Procesar datos
            df = process_csv_data(temp_path)
            if df is None:
                return False

            # Guardar en base de datos
            db = get_db()
            try:
                # Limpiar tabla existente
                db.query(Producto).delete()

                # Insertar nuevos productos
                for _, row in df.iterrows():
                    producto = Producto(
                        nombre=str(row['producto']),
                        referencia=str(row['referencia']),
                        codigo=str(row['codigo']),
                        cantidad=int(row['cantidad']),
                        precio=float(row['precio'])
                    )
                    db.add(producto)

                db.commit()
                return True
            except Exception as e:
                print(f"Error al guardar en la base de datos: {e}")
                db.rollback()
                return False
            finally:
                db.close()

        finally:
            os.unlink(temp_path)

    except Exception as e:
        print(f"Error al importar archivo: {e}")
        return False

def initialize_database():
    """Initialize database and create tables"""
    return init_db()

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