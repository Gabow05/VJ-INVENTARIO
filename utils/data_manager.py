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
                            sep=';',  # Usar punto y coma como separador
                            dtype=str  # Leer todo como string inicialmente
                        )
                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error con codificación {encoding}: {e}")
                        continue
                else:
                    raise ValueError("No se pudo leer el archivo con ninguna codificación")

            # Mapear columnas según el formato del archivo
            column_mappings = {
                # CSV UFT format
                'nombre': 'producto',
                'refer': 'referencia',
                'q_fin': 'cantidad',
                'pvta1i': 'precio',
                'codigo': 'codigo',
                'categoria': 'categoria',
                # Agregar más mapeos según otros formatos
            }

            # Renombrar columnas si existen
            for old_col, new_col in column_mappings.items():
                if old_col in df.columns:
                    df[new_col] = df[old_col]

            # Asegurar columnas requeridas
            required_columns = ['producto', 'cantidad', 'precio', 'codigo']

            # Si no existe la columna producto pero existe nombre, usar nombre
            if 'producto' not in df.columns and 'nombre' in df.columns:
                df['producto'] = df['nombre']

            # Si no existe categoría, usar una por defecto
            if 'categoria' not in df.columns:
                df['categoria'] = 'General'

            # Verificar columnas requeridas
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"Columnas requeridas no encontradas. Columnas presentes: {df.columns.tolist()}")

            # Limpiar datos
            df = df.dropna(subset=['producto'])  # Solo eliminar filas sin producto

            # Convertir y limpiar tipos de datos
            df['cantidad'] = pd.to_numeric(df['cantidad'].str.replace(r'[^\d.-]', '', regex=True), errors='coerce')
            df['cantidad'] = df['cantidad'].fillna(0).astype(int)

            df['precio'] = pd.to_numeric(df['precio'].str.replace(r'[^\d.-]', '', regex=True), errors='coerce')
            df['precio'] = df['precio'].fillna(0).astype(float)

            # Seleccionar y ordenar columnas
            final_columns = ['producto', 'categoria', 'cantidad', 'precio', 'codigo']
            df = df[final_columns]

            return save_data(df)

        finally:
            # Limpiar archivo temporal
            os.unlink(temp_path)

    except Exception as e:
        print(f"Error al procesar archivo: {str(e)}")
        return False