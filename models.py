from typing import Optional, List
from datetime import datetime
from pydantic import Field, validator
from sqlmodel import SQLModel, Field, Relationship
import re

## Modelo Auto
# Modelo Base
class AutoBase(SQLModel):
    marca: str=Field(index=True)
    modelo: str
    anio: int=Field(ge=1990, le=datetime.now().year)
    numero_chasis: str = Field(unique=True, index=True)

    @validator('numero_chasis')
    def check_alphanumeric_chasis(cls, value):
        if not re.fullmatch(r'^[a-zA-Z0-9]+$', value):
            raise ValueError("El número de chasis debe ser estrictamente alfanumérico (solo letras y números).")
        return value

# Modelo Creación
class AutoCreate(AutoBase):
    pass

# Modelo para Actualización
class AutoUpdate(SQLModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = Field(None, ge=1990, le=datetime.now().year)
    numero_chasis: Optional[str] = None

## Modelo Venta
# Modelo Base 
class VentaBase(SQLModel):
    nombre_comprador: str
    precio: float = Field(gt=0)
    fecha_venta: datetime = Field(default_factory=datetime.now)
    auto_id: int = Field(foreign_key="auto.id", index=True)

    @validator('nombre_comprador')
    def comprador_no_vacio(cls, value):
        if not value.strip():
            raise ValueError("El nombre del comprador no puede estar vacío.")
        return value
    
    @validator('fecha_venta')
    def fecha_no_futura(cls,value):
        if value > datetime.now():
            raise ValueError("La fecha de venta no puede ser mayor al día de hoy.")
        return value
    
# Modelo para Creación 
class VentaCreate(VentaBase):
    pass

# Modelo para Actualización 
class VentaUpdate(SQLModel):
    nombre_comprador: Optional[str] = None
    precio: Optional[float] = Field(None, gt=0)
    fecha_venta: Optional[datetime] = None

# Modelos de Tablas y relaciones
class Venta(VentaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    auto: "Auto" = Relationship(back_populates="ventas") # Relación Many-to-one

class Auto(AutoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ventas: List[Venta] = Relationship(
        back_populates="auto",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan"
        }
    ) # Relación One-to-many

# Modelos de respuesta API
class VentaResponse(VentaBase):
    id: int

    class Config:
        from_attributes: True

class AutoResponse(AutoBase):
    id: int

    class Config:
        from_attributes: True

class AutoResponseWithVentas(AutoResponse):
    ventas: List[VentaResponse] = []

class VentaResponseWithAuto(VentaResponse):
    auto: AutoResponse


