import pandas as pd
import os
from .models import get_db, Producto, Venta, init_db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import tempfile

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

def import_file_to_db(uploaded_file):
    """
    Import data from various file formats (CSV, Excel) to database
    """
    try:
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()

        # Save uploaded file to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name

        try:
            if file_extension in ['.xlsx', '.xls']:
                print(f"Leyendo archivo Excel")
                df = pd.read_excel(temp_path)
            else:  # CSV
                # Lista de codificaciones para CSV
                encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
                for encoding in encodings:
                    try:
                        print(f"Intentando leer CSV con codificación: {encoding}")
                        df = pd.read_csv(
                            temp_path,
                            encoding=encoding,
                            dtype={
                                'producto': str,
                                'categoria': str,
                                'cantidad': str,
                                'precio': str,
                                'codigo': str
                            }
                        )
                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error con codificación {encoding}: {e}")
                        continue
                else:
                    raise ValueError("No se pudo leer el archivo con ninguna codificación")

            # Validar y limpiar columnas
            required_columns = ['producto', 'categoria', 'cantidad', 'precio', 'codigo']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"Columnas requeridas no encontradas. Columnas presentes: {df.columns.tolist()}")

            # Limpiar datos
            df = df.dropna(subset=required_columns)

            # Convertir y limpiar tipos de datos
            df['cantidad'] = pd.to_numeric(df['cantidad'].str.replace(r'[^\d.-]', '', regex=True), errors='coerce')
            df['cantidad'] = df['cantidad'].fillna(0).astype(int)

            df['precio'] = pd.to_numeric(df['precio'].str.replace(r'[^\d.-]', '', regex=True), errors='coerce')
            df['precio'] = df['precio'].fillna(0).astype(float)

            return save_data(df)

        finally:
            # Limpiar archivo temporal
            os.unlink(temp_path)

    except Exception as e:
        print(f"Error al procesar archivo: {str(e)}")
        return False