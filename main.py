# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_db_and_tables
from autos import router as autos_router
from ventas import router as ventas_router

# --- Ciclo de Vida de la Aplicación ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación. Creando tablas de la base de datos...")
    create_db_and_tables()
    yield
    print("Apagando aplicación.")

app = FastAPI(
    title="API CRUD de Ventas de Autos (UTN Prog IV)",
    description="API REST completa para la gestión de ventas de autos, usando FastAPI, SQLModel y PostgreSQL.",
    version="1.0.0",
    lifespan=lifespan
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(autos_router)
app.include_router(ventas_router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "API de Ventas de Autos activa. Visita /docs para ver la documentación."}