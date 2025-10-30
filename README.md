# API CRUD de Ventas de Autos 🚗

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

## Ejecución de la API

Una vez que la base de datos y el entorno están configurados, puede iniciar el servidor.

**Comando de Ejecución:**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
## Endpoints y Funcionalidades Implementadas

La API implementa todos los *endpoints* CRUD requeridos y las funcionalidades de búsqueda/filtrado, cumpliendo con la especificación del trabajo práctico:

| Entidad | Método | Endpoint | Descripción |
| :--- | :--- | :--- | :--- |
| **Auto** | `POST` | `/autos/` | Crea un nuevo auto. |
| **Auto** | `GET` | `/autos/` | Listado con **Paginación** (`skip`, `limit`) y **Filtros** (`marca`, `modelo`). |
| **Auto** | `PUT` | `/autos/{auto_id}` | Actualiza un auto. |
| **Auto** | `DELETE`| `/autos/{auto_id}` | Elimina el auto. **Implementa CASCADE DELETE** (borra las ventas asociadas). |
| **Auto** | `GET` | `/autos/chasis/{numero_chasis}` | Búsqueda por número de chasis. |
| **Relación**| `GET` | `/autos/{auto_id}/with-ventas` | Obtiene el auto y su lista de ventas asociadas. |
| **Venta** | `POST` | `/ventas/` | Crea una nueva venta. (Requiere `auto_id` existente) |
| **Venta** | `GET` | `/ventas/` | Listado con **Filtros** por rango de **Precio** (`min_precio`, `max_precio`) y **Fecha**. |
| **Venta** | `GET` | `/ventas/comprador/{nombre}` | Búsqueda por nombre de comprador (parcial). |
| **Relación**| `GET` | `/ventas/{venta_id}/with-auto` | Obtiene la venta con la información completa del auto. |

## Ejemplos de Uso de la API

Los siguientes ejemplos utilizan el puerto 8080, según la configuración de desarrollo

1. **Crear un Auto:**
POST http://localhost:8080/autos/
### Body (JSON):
{
    "marca": "Chevrolet",
    "modelo": "Cruze",
    "anio": 2024,
    "numero_chasis": "CHV2024CRZ789012"
}

2. **Crear una Venta:**
POST http://localhost:8080/ventas/
### Body (JSON):
{
    "nombre_comprador": "María Giménez",
    "precio": 35500.00,
    "auto_id": 1,
    "fecha_venta": "2025-10-29T11:55:00"
}

3. **Obtener Auto con Ventas Relacionadas:**
GET http://localhost:8080/autos/1/with-ventas
