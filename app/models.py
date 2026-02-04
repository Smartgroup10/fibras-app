from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="viewer")  # admin, editor, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Linea(Base):
    __tablename__ = "lineas"

    id = Column(Integer, primary_key=True, index=True)
    numero_linea = Column(String(50), unique=True, index=True, nullable=False)
    proveedor = Column(String(50), index=True, default="Movistar")  # Movistar, LCR
    servicio_conectividad = Column(String(100))
    sede = Column(Text)
    tipo_conectividad = Column(String(50), index=True)
    velocidad_conexion = Column(String(50))
    tipo_ip = Column(String(20), index=True)
    tipo_mantenimiento = Column(String(100))
    cliente = Column(String(200))  # Nombre del cliente
    direccion_ip = Column(String(50))  # IP asignada
    notas = Column(Text)  # Campo de notas libre
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
