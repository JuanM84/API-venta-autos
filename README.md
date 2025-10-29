# API CRUD de Ventas de Autos

API REST gestión de ventas de autos

## Tecnologías Utilizadas

* **Framework:** FastAPI
* **ORM:** SQLModel
* **Base de Datos:** PostgreSQL
* **Lenguaje:** Python
* **Validaciones y Serialización:** Pydantic

---

## Configuración e Instalación

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local.

### 1. Requisitos Previos

* **Python 3.10+**
* **PostgreSQL Server** (Versión 12 o superior)

### 2. Base de Datos

1.  **Crear la base de datos:** Conectarse a tu servidor PostgreSQL (usando `psql` o pgAdmin) y crear la base de datos necesaria:
    ```sql
    CREATE DATABASE autos_db;
    ```
2.  **Configurar Credenciales:** Crear un archivo llamado **`.env`** en la raíz del proyecto y añadir la URL de conexión, reemplazando el `usuario` y `password` con sus credenciales de PostgreSQL:

    ```text
    DATABASE_URL=postgresql://usuario:password@localhost:5432/autos_db
    ```

### 3. Entorno Python

1.  **Clonar el repositorio** (si aplica) y navegar a la carpeta raíz del proyecto.
2.  **Crear y Activar el Entorno Virtual:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate   # En Windows
    source venv/bin/activate  # En Linux/macOS
    ```
3.  **Instalar Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

---

## ▶️ Ejecución de la API

Una vez que la base de datos y el entorno están configurados, puede iniciar el servidor.

**Comando de Ejecución:**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000