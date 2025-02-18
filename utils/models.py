from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime

# Configuración de la URL de la base de datos con SSL
database_url = os.environ['DATABASE_URL']
if "?" in database_url:
    database_url += "&sslmode=require"
else:
    database_url += "?sslmode=require"

Base = declarative_base()

class Producto(Base):
    __tablename__ = 'productos'

    id = Column(Integer, primary_key=True)
    codigo = Column(String, unique=True, nullable=False)
    nombre = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    cantidad = Column(Integer, default=0)
    precio = Column(Float, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow)

class Venta(Base):
    __tablename__ = 'ventas'

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey('productos.id'))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)

    producto = relationship("Producto")

# Configuración de la base de datos
engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db():
    """Inicializa la base de datos creando todas las tablas necesarias"""
    try:
        Base.metadata.create_all(engine)
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def get_db():
    """
    Crea y retorna una nueva sesión de base de datos.
    La sesión debe ser cerrada por el llamador cuando termine de usarla.
    """
    return SessionLocal()
