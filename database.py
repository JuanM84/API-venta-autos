import os
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, SQLModel

# Variables de Entorno
load_dotenv()

# Dirección de la DB
DATABASE_URL = os.environ.get("DATABASE_URL")
print("DATABASE_URL =>", repr(DATABASE_URL))


if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada en el entorno o .env")

# Motor de la DB
engine = create_engine(
    DATABASE_URL, 
    echo=True,
    connect_args={ "options": "-c client_encoding=utf8"}

)

# Creación de DB y Tablas
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("Base de datos y tablas creadas exitosamente.")

@contextmanager
def get_session_context():
    session = Session(engine)
    try:
        yield session
    except Exception as e:
        session.rollback()
        print(f"Error en la sesión. Rollback ejecutado: {e}")
        raise
    finally:
        session.close

def get_session():
    with get_session_context() as session:
        yield session 