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
            'referencia': p.codigo,
            'cantidad': p.cantidad,
            'precio': p.precio,
            'codigo': p.codigo
        } for p in productos]
        return pd.DataFrame(data) if data else pd.DataFrame(
            columns=['producto', 'referencia', 'cantidad', 'precio', 'codigo']
        )
    except SQLAlchemyError as e:
        print(f"Error loading data: {e}")
        return None
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
                df = pd.read_excel(temp_path)
            else:  # CSV
                encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
                for encoding in encodings:
                    try:
                        print(f"Intentando leer CSV con codificación: {encoding}")
                        df = pd.read_csv(
                            temp_path,
                            encoding=encoding,
                            sep=';',
                            dtype=str
                        )
                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error con codificación {encoding}: {e}")
                        continue
                else:
                    raise ValueError("No se pudo leer el archivo con ninguna codificación")

            # Mapear columnas específicas del archivo CSV UFT
            df = df.rename(columns={
                'nombre': 'producto',
                'refer': 'referencia',
                'codigo': 'codigo',
                'q_fin': 'cantidad',
                'pvta1i': 'precio'
            })

            # Verificar columnas requeridas
            required_columns = ['producto', 'cantidad', 'precio']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Faltan columnas requeridas: {missing_columns}")

            # Limpiar y convertir datos
            df['cantidad'] = pd.to_numeric(df['cantidad'].fillna('0').astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce').fillna(0).astype(int)
            df['precio'] = pd.to_numeric(df['precio'].fillna('0').astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce').fillna(0).astype(float)

            # Asegurar que el código sea string
            df['codigo'] = df['codigo'].fillna('').astype(str)

            # Preparar datos para la base de datos
            db = get_db()
            try:
                # Limpiar tabla existente
                db.query(Producto).delete()

                # Insertar nuevos productos
                for _, row in df.iterrows():
                    producto = Producto(
                        nombre=str(row['producto']),
                        codigo=str(row['codigo']),
                        categoria='General',  # Categoría por defecto
                        cantidad=int(row['cantidad']),
                        precio=float(row['precio']),
                        fecha_actualizacion=datetime.now()
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
            # Limpiar archivo temporal
            os.unlink(temp_path)

    except Exception as e:
        print(f"Error al procesar archivo: {str(e)}")
        return False

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