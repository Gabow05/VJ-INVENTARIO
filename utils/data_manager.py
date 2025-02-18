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

def import_file_to_db(file_path):
    """
    Import data from various file formats (CSV, Excel) to database
    """
    file_extension = os.path.splitext(file_path)[1].lower()

    # Lista de codificaciones para CSV
    encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']

    try:
        if file_extension in ['.xlsx', '.xls']:
            print(f"Leyendo archivo Excel: {file_path}")
            df = pd.read_excel(file_path)
        else:  # Intentar leer como CSV con diferentes codificaciones
            for encoding in encodings:
                try:
                    print(f"Intentando leer CSV con codificación: {encoding}")
                    df = pd.read_csv(
                        file_path,
                        encoding=encoding,
                        dtype={
                            'producto': str,
                            'categoria': str,
                            'cantidad': str,  # Cambiado a str para manejar formato flexible
                            'precio': str,    # Cambiado a str para manejar formato flexible
                            'codigo': str
                        }
                    )
                    break
                except UnicodeDecodeError:
                    print(f"Error de codificación con {encoding}")
                    continue
                except Exception as e:
                    print(f"Error al procesar archivo con {encoding}: {str(e)}")
                    continue
            else:
                print("No se pudo leer el archivo con ninguna codificación")
                return False

        # Validar y limpiar columnas
        required_columns = ['producto', 'categoria', 'cantidad', 'precio', 'codigo']
        if not all(col in df.columns for col in required_columns):
            print(f"Columnas requeridas no encontradas. Columnas presentes: {df.columns.tolist()}")
            return False

        # Limpiar datos
        df = df.dropna(subset=required_columns)

        # Convertir y limpiar tipos de datos
        try:
            # Limpiar cantidad (remover caracteres no numéricos)
            df['cantidad'] = pd.to_numeric(df['cantidad'].str.replace(r'[^\d.-]', '', regex=True), errors='coerce')
            df['cantidad'] = df['cantidad'].fillna(0).astype(int)

            # Limpiar precio (remover caracteres no numéricos excepto punto decimal)
            df['precio'] = pd.to_numeric(df['precio'].str.replace(r'[^\d.-]', '', regex=True), errors='coerce')
            df['precio'] = df['precio'].fillna(0).astype(float)
        except Exception as e:
            print(f"Error al convertir tipos de datos: {e}")
            return False

        print("Archivo procesado exitosamente")
        return save_data(df)

    except Exception as e:
        print(f"Error al procesar archivo: {str(e)}")
        return False