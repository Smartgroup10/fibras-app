from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: str
    role: str = "viewer"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Auth schemas
class LoginForm(BaseModel):
    username: str
    password: str

# Linea schemas
class LineaBase(BaseModel):
    numero_linea: str
    proveedor: str = "Movistar"
    servicio_conectividad: Optional[str] = None
    sede: Optional[str] = None
    tipo_conectividad: Optional[str] = None
    velocidad_conexion: Optional[str] = None
    tipo_ip: Optional[str] = None
    tipo_mantenimiento: Optional[str] = None
    cliente: Optional[str] = None
    direccion_ip: Optional[str] = None
    notas: Optional[str] = None

class LineaCreate(LineaBase):
    pass

class LineaUpdate(BaseModel):
    numero_linea: Optional[str] = None
    proveedor: Optional[str] = None
    servicio_conectividad: Optional[str] = None
    sede: Optional[str] = None
    tipo_conectividad: Optional[str] = None
    velocidad_conexion: Optional[str] = None
    tipo_ip: Optional[str] = None
    tipo_mantenimiento: Optional[str] = None
    cliente: Optional[str] = None
    direccion_ip: Optional[str] = None
    notas: Optional[str] = None

class LineaResponse(LineaBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
