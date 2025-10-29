from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from models import (
    VentaCreate, VentaResponse, VentaUpdate, VentaResponseWithAuto
)
from repository import (
    PostgresVentaRepository, NotFoundException, IntegrityError
)
from database import get_session

router = APIRouter(prefix="/ventas", tags=["Ventas"])


def get_venta_repo(session: Session = Depends(get_session)) -> PostgresVentaRepository:
    """Proporciona una instancia del repositorio de Venta."""
    return PostgresVentaRepository(session)

# Endpoints

@router.post(
    "/",
    response_model=VentaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva Venta"
)
def create_venta(
    venta: VentaCreate,
    repo: PostgresVentaRepository = Depends(get_venta_repo)
):
    """
    Registra una nueva venta de vehículo.

    - **Valida** que el `auto_id` referencie un auto existente.
    - **Valida** que el precio sea mayor a 0 y la fecha no sea futura.
    """
    try:
        return repo.create(venta)
    except (NotFoundException, IntegrityError) as e:
        raise e

@router.get(
    "/",
    response_model=List[VentaResponse],
    summary="Listar Ventas con Paginación y Filtros"
)
def list_ventas(
    repo: PostgresVentaRepository = Depends(get_venta_repo),
    skip: int = Query(0, ge=0, description="Número de registros a omitir (Paginación)"),
    limit: int = Query(100, le=1000, description="Número máximo de registros a devolver"),
    min_precio: Optional[float] = Query(None, ge=0, description="Filtro por precio mínimo"),
    max_precio: Optional[float] = Query(None, ge=0, description="Filtro por precio máximo"),
    fecha_inicio: Optional[datetime] = Query(None, description="Filtro por rango de fechas (Inicio)"),
    fecha_fin: Optional[datetime] = Query(None, description="Filtro por rango de fechas (Fin)"),
):
    """
    Obtiene la lista de ventas con paginación y filtros por rango de precios o fechas.
    """
    return repo.get_all(
        skip=skip,
        limit=limit,
        min_precio=min_precio,
        max_precio=max_precio,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )

@router.get(
    "/{venta_id}",
    response_model=VentaResponse,
    summary="Obtener Venta por ID"
)
def get_venta(
    venta_id: int,
    repo: PostgresVentaRepository = Depends(get_venta_repo)
):
    """Busca y retorna una venta específica por su ID."""
    try:
        return repo.get_by_id(venta_id)
    except NotFoundException as e:
        raise e

@router.put(
    "/{venta_id}",
    response_model=VentaResponse,
    summary="Actualizar Venta"
)
def update_venta(
    venta_id: int,
    venta_update: VentaUpdate,
    repo: PostgresVentaRepository = Depends(get_venta_repo)
):
    """Actualiza la información de una venta existente."""
    try:
        return repo.update(venta_id, venta_update)
    except NotFoundException as e:
        raise e

@router.delete(
    "/{venta_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar Venta"
)
def delete_venta(
    venta_id: int,
    repo: PostgresVentaRepository = Depends(get_venta_repo)
):
    """Elimina una venta por su ID."""
    if not repo.delete(venta_id):
        raise NotFoundException(f"Venta con ID {venta_id} no encontrada para eliminar")
    return

@router.get(
    "/auto/{auto_id}",
    response_model=List[VentaResponse],
    summary="Ventas por ID de Auto"
)
def get_ventas_by_auto_id(
    auto_id: int,
    repo: PostgresVentaRepository = Depends(get_venta_repo)
):
    """Lista todas las ventas asociadas a un ID de auto específico."""
    return repo.get_by_auto_id(auto_id)

@router.get(
    "/comprador/{nombre}",
    response_model=List[VentaResponse],
    summary="Ventas por Nombre de Comprador"
)
def get_ventas_by_comprador(
    nombre: str,
    repo: PostgresVentaRepository = Depends(get_venta_repo)
):
    """Busca ventas por el nombre del comprador (búsqueda parcial)."""
    return repo.get_by_comprador(nombre)

@router.get(
    "/{venta_id}/with-auto",
    response_model=VentaResponseWithAuto,
    summary="Venta con Información de Auto"
)
def get_venta_with_auto(
    venta_id: int,
    repo: PostgresVentaRepository = Depends(get_venta_repo)
):
    """Retorna una venta junto con la información completa del auto vendido."""
    try:
        venta = repo.get_by_id(venta_id)
        return venta
    except NotFoundException as e:
        raise e