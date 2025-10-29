from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlmodel import Session

from models import ( AutoCreate, AutoResponse, AutoUpdate, AutoResponseWithVentas, VentaResponse )

from repository import ( PostgresAutoRepository, NotFoundException, IntegrityError )

from database import get_session

router = APIRouter(prefix="/autos", tags=["Autos"])

def get_auto_repo(session: Session = Depends(get_session)) -> PostgresAutoRepository:
    """Proporciona una instancia del repositorio de Auto."""
    return PostgresAutoRepository(session)

# Endpoints

@router.post(
    "/",
    response_model=AutoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo Auto"
)
def create_auto(
    auto: AutoCreate,
    repo: PostgresAutoRepository = Depends(get_auto_repo)
):
    """
    Registra un nuevo vehículo en el inventario.
    - **Valida** que el número de chasis sea único.
    - **Valida** el rango de año de fabricación.
    """
    try:
        return repo.create(auto)
    except IntegrityError as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get(
    "/",
    response_model=List[AutoResponse],
    summary="Listar Autos con Paginación y Búsqueda"
)
def list_autos(
    repo: PostgresAutoRepository = Depends(get_auto_repo),
    skip: int = Query(0, ge=0, description="Número de registros a omitir (Paginación)"),
    limit: int = Query(100, le=1000, description="Número máximo de registros a devolver"),
    marca: Optional[str] = Query(None, description="Buscar por marca (parcial)"),
    modelo: Optional[str] =  Query(None, description="Buscar por modelo (parcial)"),  
):
    """
    Obtiene la lista de autos, permitiendo paginación y filtros por marca/modelo.
    """
    return repo.get_all(skip=skip, limit=limit, marca=marca, modelo=modelo)

@router.get(
    "/{auto_id}",
    response_model=AutoResponse,
    summary="Obtener Auto por ID"
)
def get_auto(
    auto_id: int,
    repo: PostgresAutoRepository = Depends(get_auto_repo)
):
    """Buscar y retorna un auto específico por su ID."""
    try:
        return repo.get_by_id(auto_id)
    except NotFoundException as e:
        raise e
    
@router.put(
    "/{auto_id}",
    response_model=AutoResponse,
    summary="Actualizar Auto"
)
def update_auto(
    auto_id: int,
    auto_update: AutoUpdate,
    repo: PostgresAutoRepository = Depends(get_auto_repo)
):
    """Actualiza la información de un auto existente."""
    try:
        return repo.update(auto_id, auto_update)
    except (NotFoundException, IntegrityError) as e:
        raise e
    
@router.delete(
    "/{auto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar Auto"
)
def delete_auto(
    auto_id: int,
    repo: PostgresAutoRepository = Depends(get_auto_repo)
):
    """Elimina un auto por su ID."""
    if not repo.delete(auto_id):
        raise NotFoundException(f"Auto con ID {auto_id} no encontrado para eliminar")
    return

@router.get(
    "/chasis/{numero_chasis}",
    response_model=AutoResponse,
    summary="Buscar Auto por Número de Chasis"
)
def get_auto_by_chasis(
    numero_chasis: str,
    repo: PostgresAutoRepository = Depends(get_auto_repo)
):
    """Busca un auto específico por su número de chasis único."""
    auto = repo.get_by_chasis(numero_chasis)
    if not auto:
        raise NotFoundException(f"Auto con chasis {numero_chasis} no encontrado")
    return auto

@router.get(
    "/{auto_id}/with-ventas",
    response_model=AutoResponseWithVentas,
    summary="Obtener Auto con su Historial de Ventas"
)
def get_auto_with_ventas(
    auto_id: int,
    repo: PostgresAutoRepository = Depends(get_auto_repo)
):
    """Retorna un auto junto con la lista completa de ventas asociadas."""
    try:
        auto = repo.get_by_id(auto_id)
        return auto
    except NotFoundException as e:
        raise e