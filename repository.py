from typing import Optional, List, Protocol
from datetime import datetime
from sqlmodel import Session, select, func
from pydantic import ValidationError
from models import Auto, Venta, AutoCreate, AutoUpdate, VentaCreate, VentaUpdate
from fastapi import HTTPException, status

# Excepciones
class NotFoundException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    
class IntegrityError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

# Interfaces
class AutoRepository(Protocol):
    def create(self, auto: AutoCreate) -> Auto: ...
    def get_by_id(self, auto_id: int) -> Optional[Auto]: ...
    def get_all(self, skip: int,limit: int, marca: Optional[str] = None, modelo: Optional[str] = None ) -> List[Auto]: ...
    def update(self, auto_id: int, auto_update: AutoUpdate) -> Optional[Auto]: ...
    def delete(self, auto_id: int) -> bool: ...
    def get_by_chasis(self, numero_chasis:str) -> Optional[Auto]: ...

class VentaRepository(Protocol):
    def create(self, venta: VentaCreate) -> Venta: ...
    def get_by_id(self, venta_id: int) -> Optional[Venta]: ...
    def get_all(self, skip: int, limit: int, min_precio: Optional[float] = None, max_precio: Optional[float] = None, fecha_inicio: Optional[datetime] = None,fecha_fin: Optional[datetime] = None) -> List[Venta]: ...
    def update(self, venta_id: int, venta_update: VentaUpdate) -> Optional[Venta]: ...
    def delete(self, venta_id: int) -> bool: ...
    def get_by_auto_id(self, auto_id: int) -> List[Venta]: ...
    def get_by_comprador(self, nombre: str) -> List[Venta]: ...
    
# Clases
class PostgresAutoRepository:
    
    def __init__(self, session: Session):
        self.session = session 
    
    def create(self, auto:AutoCreate) -> Auto:
        if self.get_by_chasis(auto.numero_chasis):
            raise IntegrityError(f"Ya existe un auto con el número de chasis: {auto.numero_chasis}")
        
        db_auto = Auto.model_validate(auto)
        try:
            self.session.add(db_auto)
            self.session.commit()
            self.session.refresh(db_auto)
            return db_auto
        except Exception as e:
            self.session.rollback()
            raise IntegrityError(f"Error al crear el auto: {e}")
    
    def get_by_id(self, auto_id: int) -> Optional[Auto]:
        statement = select(Auto).where(Auto.id == auto_id)
        result = self.session.exec(statement).first()
        if not result:
            raise NotFoundException(f"Auto con ID {auto_id} no encontrado")
        return result
    
    def get_all(self, skip: int = 0, limit: int = 100, marca: Optional[str] = None, modelo: Optional[str] = None) -> List[Auto]:
        statement = select(Auto).offset(skip).limit(limit)
        if marca:
            statement = statement.where(func.lower(Auto.marca).like(f"%{marca.lower()}%"))
        if modelo:
            statement = statement.where(func.lower(Auto.modelo).like(f"%{modelo.lower()}%"))
        return self.session.exec(statement).all()
    
    def update(self, auto_id: int, auto_update: AutoUpdate) -> Auto:
        
        db_auto = self.session.get(Auto, auto_id)

        if not db_auto:
            raise NotFoundException(f"Auto con ID {auto_id} no encontrado")
        
        if auto_update.numero_chasis and auto_update.numero_chasis != db_auto.numero_chasis :
            if self.get_by_chasis(auto_update.numero_chasis):
                raise IntegrityError(f"Ya existe un auto con el número de chasis: {auto_update.numero_chasis}")
        
        for key, value in auto_update.model_dump(exclude_unset=True).items():
            setattr(db_auto, key, value)
        
        try:
            self.session.add(db_auto)
            self.session.commit()
            self.session.refresh(db_auto)
            return db_auto
        except Exception as e:
            self.session.rollback()
            raise IntegrityError(f"Error al actualizar el auto: {e}")
        
    def delete(self, auto_id: int) -> bool:
        
        db_auto = self.session.get(Auto, auto_id)

        if not db_auto:
            return False    
        self.session.delete(db_auto)
        self.session.commit()
        return True
    
    def get_by_chasis(self, numero_chasis: str) -> Optional[Auto]:
        statement = select(Auto).where(Auto.numero_chasis == numero_chasis)
        return self.session.exec(statement).first()
    
class PostgresVentaRepository:
    
    def __init__(self, session: Session):
        self.session = session
        self.auto_repo = PostgresAutoRepository(session)

    def create(self, venta: VentaCreate) -> Venta:
        
        if not self.auto_repo.session.get(Auto, venta.auto_id):
            raise NotFoundException(f"No se puede crear la venta: Auto con ID {venta.auto_id} no encontrado.")

        db_venta = Venta.model_validate(venta)
        try:
            self.session.add(db_venta)
            self.session.commit()
            self.session.refresh(db_venta)
            return db_venta
        except Exception as e:
            self.session.rollback()
            raise IntegrityError(f"Error al crear la venta: {e}")

    def get_by_id(self, venta_id: int) -> Optional[Venta]:
        statement = select(Venta).where(Venta.id == venta_id)
        result = self.session.exec(statement).first()
        if not result:
            raise NotFoundException(f"Venta con ID {venta_id} no encontrada")
        return result

    def get_all(self, skip: int = 0, limit: int = 100, min_precio: Optional[float] = None, max_precio: Optional[float] = None, fecha_inicio: Optional[datetime] = None, fecha_fin: Optional[datetime] = None) -> List[Venta]:

        statement = select(Venta).offset(skip).limit(limit)

        if min_precio is not None:
            statement = statement.where(Venta.precio >= min_precio)
        if max_precio is not None:
            statement = statement.where(Venta.precio <= max_precio)
        if fecha_inicio:
            statement = statement.where(Venta.fecha_venta >= fecha_inicio)
        if fecha_fin:
            statement = statement.where(Venta.fecha_venta <= fecha_fin)

        return self.session.exec(statement).all()

    def update(self, venta_id: int, venta_update: VentaUpdate) -> Venta:

        db_venta = self.session.get(Venta, venta_id)

        if not db_venta:
            raise NotFoundException(f"Venta con ID {venta_id} no encontrada")

        for key, value in venta_update.model_dump(exclude_unset=True).items():
            setattr(db_venta, key, value)

        try:
            self.session.add(db_venta)
            self.session.commit()
            self.session.refresh(db_venta)
            return db_venta
        except Exception as e:
            self.session.rollback()
            raise IntegrityError(f"Error al actualizar la venta: {e}")

    def delete(self, venta_id: int) -> bool:
        db_venta = self.session.get(Venta, venta_id)
        if not db_venta:
            return False

        self.session.delete(db_venta)
        self.session.commit()
        return True

    def get_by_auto_id(self, auto_id: int) -> List[Venta]:
        statement = select(Venta).where(Venta.auto_id == auto_id)
        return self.session.exec(statement).all()

    def get_by_comprador(self, nombre: str) -> List[Venta]:
        statement = select(Venta).where(func.lower(Venta.nombre_comprador).like(f"%{nombre.lower()}%"))
        return self.session.exec(statement).all()