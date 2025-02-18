import pandas as pd
import sqlite3
import os
from datetime import datetime

DB_PATH = 'inventory.db'

def initialize_database():
    """Inicializa la base de datos si no existe"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory
        (producto TEXT, referencia TEXT, codigo TEXT, cantidad INTEGER, precio REAL)
    ''')

    conn.commit()
    conn.close()

def import_file_to_db(file):
    """Importa datos desde un archivo CSV o Excel a la base de datos"""
    try:
        # Determinar el tipo de archivo
        file_extension = os.path.splitext(file.name)[1].lower()

        if file_extension == '.csv':
            # Intentar diferentes delimitadores
            try:
                df = pd.read_csv(file, encoding='utf-8')
            except:
                try:
                    df = pd.read_csv(file, encoding='utf-8', sep=';')
                except:
                    df = pd.read_csv(file, encoding='latin1', sep=';')
        elif file_extension in ['.xls', '.xlsx']:
            df = pd.read_excel(file)
        else:
            return False

        # Renombrar columnas si es necesario
        column_mapping = {
            'nombre': 'producto',
            'refer': 'referencia',
            'q_fin': 'cantidad',
            'pvta1i': 'precio'
        }

        df.rename(columns=str.lower, inplace=True)
        df.rename(columns=column_mapping, inplace=True)

        # Asegurarse de que las columnas requeridas existan
        required_columns = ['producto', 'referencia', 'codigo', 'cantidad', 'precio']
        if not all(col in df.columns for col in required_columns):
            return False

        # Limpiar y convertir datos
        df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0).astype(int)
        df['precio'] = pd.to_numeric(df['precio'], errors='coerce').fillna(0)

        # Eliminar filas con valores nulos en columnas críticas
        df = df.dropna(subset=['producto', 'codigo'])

        # Guardar en la base de datos
        conn = sqlite3.connect(DB_PATH)

        # Eliminar datos existentes
        conn.execute('DELETE FROM inventory')

        # Insertar nuevos datos
        df[required_columns].to_sql('inventory', conn, if_exists='append', index=False)

        conn.commit()
        conn.close()

        return True

    except Exception as e:
        print(f"Error al importar archivo: {str(e)}")
        return False

def load_data():
    """Carga los datos desde la base de datos"""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query('SELECT * FROM inventory', conn)
        conn.close()
        return df
    except:
        return None