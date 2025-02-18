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
    Process the CSV file with multiple encodings and formats
    """
    encodings = ['utf-8-sig', 'latin1', 'iso-8859-1', 'cp1252']
    separators = [';', ',', '\t']

    for encoding in encodings:
        for sep in separators:
            try:
                df = pd.read_csv(file_path, sep=sep, encoding=encoding, on_bad_lines='skip')

                # Try to identify and rename columns
                expected_columns = {'nombre', 'refer', 'codigo', 'q_fin', 'pvta1i'}
                actual_columns = set(df.columns)

                # Check if we have at least some of the expected columns
                if any(col in actual_columns for col in expected_columns):
                    # Rename columns according to the expected format
                    column_mapping = {
                        'nombre': 'producto',
                        'refer': 'referencia',
                        'codigo': 'codigo',
                        'q_fin': 'cantidad',
                        'pvta1i': 'precio'
                    }

                    df = df.rename(columns=column_mapping)

                    # Select needed columns, using only those that exist
                    needed_columns = ['producto', 'referencia', 'codigo', 'cantidad', 'precio']
                    existing_columns = [col for col in needed_columns if col in df.columns]
                    df = df[existing_columns]

                    # Fill missing columns with default values
                    for col in needed_columns:
                        if col not in df.columns:
                            df[col] = ''

                    # Clean and convert data
                    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0).astype(int)
                    df['precio'] = pd.to_numeric(df['precio'], errors='coerce').fillna(0).astype(float)

                    return df

            except Exception as e:
                continue

    raise Exception("No se pudo procesar el archivo. Formato no compatible.")

def process_excel_data(file_path):
    """
    Process Excel files
    """
    try:
        df = pd.read_excel(file_path, engine='openpyxl')

        # Try to identify and rename columns similar to CSV processing
        expected_columns = {'nombre', 'refer', 'codigo', 'q_fin', 'pvta1i'}
        actual_columns = set(df.columns)

        if any(col in actual_columns for col in expected_columns):
            column_mapping = {
                'nombre': 'producto',
                'refer': 'referencia',
                'codigo': 'codigo',
                'q_fin': 'cantidad',
                'pvta1i': 'precio'
            }

            df = df.rename(columns=column_mapping)

            needed_columns = ['producto', 'referencia', 'codigo', 'cantidad', 'precio']
            existing_columns = [col for col in needed_columns if col in df.columns]
            df = df[existing_columns]

            for col in needed_columns:
                if col not in df.columns:
                    df[col] = ''

            df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0).astype(int)
            df['precio'] = pd.to_numeric(df['precio'], errors='coerce').fillna(0).astype(float)

            return df

    except Exception as e:
        raise Exception(f"Error processing Excel file: {str(e)}")

def import_file_to_db(uploaded_file):
    """
    Import data from file to database
    """
    try:
        # Save temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1].lower()) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name

        try:
            # Process based on file extension
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            if file_ext in ['.csv']:
                df = process_csv_data(temp_path)
            elif file_ext in ['.xls', '.xlsx']:
                df = process_excel_data(temp_path)
            else:
                raise Exception("Formato de archivo no soportado")

            if df is None:
                return False

            # Save to database
            db = get_db()
            try:
                # Clean existing table
                db.query(Producto).delete()

                # Insert new products
                for _, row in df.iterrows():
                    # Asegurar que el código mantenga los ceros iniciales
                    codigo = str(row['codigo']).zfill(5) if pd.notna(row['codigo']) else ''
                    producto = Producto(
                        nombre=str(row['producto']),
                        referencia=str(row['referencia']),
                        codigo=codigo,
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
            # Asegurar que el código mantenga los ceros iniciales
            codigo = str(row['codigo']).zfill(5) if pd.notna(row['codigo']) else ''
            producto = Producto(
                nombre=row['producto'],
                referencia=row['referencia'],
                codigo=codigo,
                cantidad=int(row['cantidad']),
                precio=float(row['precio'])
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