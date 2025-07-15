# EFC V2 Backend API

Sistema backend para la gestión de **Expedientes Electrónicos de Comercio Exterior** construido con **Django REST Framework**. Este sistema permite la administración completa de pedimentos aduanales, documentos digitales, organizaciones y usuarios en el ámbito del comercio exterior mexicano.

## 🚀 Características Principales

- **🔐 Autenticación JWT**: Sistema seguro de autenticación con tokens JWT
- **📋 Gestión de Pedimentos**: CRUD completo para pedimentos aduanales
- **📁 Gestión de Documentos**: Subida, descarga y administración de documentos
- **🏢 Multi-organización**: Soporte para múltiples organizaciones con aislamiento de datos
- **👥 Gestión de Usuarios**: Sistema de usuarios con roles y permisos
- **📊 Logging y Auditoría**: Sistema completo de logs y monitoreo
- **🔄 Integración VUCEM**: Conexión con sistemas externos
- **📑 Documentación API**: Swagger/OpenAPI automática
- **🔍 Filtros Avanzados**: Búsqueda, filtrado y paginación

## 🛠️ Tecnologías

- **Framework**: Django 5.2.3 + Django REST Framework 3.16.0
- **Base de Datos**: PostgreSQL (con psycopg2-binary)
- **Autenticación**: JWT (djangorestframework-simplejwt)
- **Documentación**: drf-yasg (Swagger/OpenAPI)
- **Filtros**: django-filter
- **CORS**: django-cors-headers
- **Archivos**: Pillow para manejo de imágenes

## 📁 Estructura del Proyecto

```
backend/
├── api/                          # Aplicaciones de la API
│   ├── customs/                  # Gestión de aduanas y pedimentos
│   ├── record/                   # Gestión de documentos
│   ├── organization/             # Gestión de organizaciones
│   ├── cuser/                    # Gestión de usuarios personalizados
│   ├── licence/                  # Gestión de licencias
│   ├── datastage/                # Etapas de datos
│   ├── vucem/                    # Integración VUCEM
│   ├── logger/                   # Sistema de logging
│   └── notificaciones/           # Sistema de notificaciones
├── config/                       # Configuración de Django
│   ├── settings.py              # Configuración principal
│   ├── urls.py                  # URLs principales
│   └── wsgi.py                  # WSGI configuration
├── core/                        # Utilidades y permisos centrales
├── media/                       # Archivos subidos
├── static/                      # Archivos estáticos
├── logs/                        # Archivos de log
├── requirements.txt             # Dependencias
├── manage.py                   # Django management script
└── Dockerfile                  # Docker configuration
```

## ⚙️ Instalación y Configuración

### Requisitos Previos

- Python 3.11+
- PostgreSQL
- Git

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd EFC_V2/backend
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

Crear una base de datos PostgreSQL y configurar las variables de entorno o editar `config/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'efc_db',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Ejecutar Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 7. Ejecutar Servidor de Desarrollo

```bash
python manage.py runserver 0.0.0.0:8000
```

## 🐳 Docker

### Ejecutar con Docker

```bash
# Construir imagen
docker build -t efc-backend .

# Ejecutar contenedor
docker run -p 8000:8000 efc-backend
```

## 📚 API Endpoints

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/token/` | Obtener token JWT |
| POST | `/api/v1/token/refresh/` | Renovar token JWT |

### Pedimentos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/customs/pedimentos/` | Listar pedimentos |
| POST | `/api/v1/customs/pedimentos/` | Crear pedimento |
| GET | `/api/v1/customs/pedimentos/{id}/` | Obtener pedimento |
| PUT | `/api/v1/customs/pedimentos/{id}/` | Actualizar pedimento |
| DELETE | `/api/v1/customs/pedimentos/{id}/` | Eliminar pedimento |

### Documentos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/record/documents/` | Listar documentos |
| POST | `/api/v1/record/documents/` | Subir documento |
| GET | `/api/v1/record/documents/{id}/` | Obtener documento |
| GET | `/api/v1/record/documents/descargar/{id}/` | Descargar documento |
| POST | `/api/v1/record/documents/bulk-download/` | Descarga masiva ZIP |

### Organizaciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/organization/organizaciones/` | Listar organizaciones |
| POST | `/api/v1/organization/organizaciones/` | Crear organización |

### Usuarios

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/user/users/` | Listar usuarios |
| GET | `/api/v1/user/users/me/` | Perfil del usuario actual |
| POST | `/api/v1/user/users/` | Crear usuario |

### Catálogos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/customs/aduanas/` | Catálogo de aduanas |
| GET | `/api/v1/customs/agentesaduanales/` | Agentes aduanales |
| GET | `/api/v1/customs/tiposoperacion/` | Tipos de operación |
| GET | `/api/v1/customs/regimenes/` | Regímenes aduanales |

## 🔐 Autenticación

El sistema utiliza **JWT (JSON Web Tokens)** para autenticación:

### 1. Obtener Token

```bash
curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "tu_usuario", "password": "tu_contraseña"}'
```

### 2. Usar Token

```bash
curl -X GET http://localhost:8000/api/v1/customs/pedimentos/ \
  -H "Authorization: Bearer tu_token_jwt"
```

## 🔍 Filtros y Búsqueda

La API soporta filtros avanzados en la mayoría de endpoints:

### Ejemplos de Filtros

```bash
# Filtrar pedimentos por patente
GET /api/v1/customs/pedimentos/?patente=1234

# Búsqueda por texto
GET /api/v1/customs/pedimentos/?search=contribuyente

# Ordenamiento
GET /api/v1/customs/pedimentos/?ordering=-created_at

# Paginación
GET /api/v1/customs/pedimentos/?page=2&page_size=10
```

## 📊 Sistema de Logging

El sistema incluye un completo sistema de logging y auditoría:

### Tipos de Logs

- **Request Logs**: Todas las peticiones HTTP
- **User Activity**: Actividades de usuarios
- **Error Logs**: Errores del sistema

### Endpoints de Logging

```bash
# Ver estadísticas de requests
GET /api/v1/logger/requests/statistics/

# Ver logs de actividad
GET /api/v1/logger/activities/

# Ver logs de errores
GET /api/v1/logger/errors/
```

## 🧪 Testing

```bash
# Ejecutar tests
python manage.py test

# Ejecutar tests con coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📖 Documentación API

### Swagger UI
Accede a la documentación interactiva:
- **Swagger**: http://localhost:8000/api/v1/swagger/
- **ReDoc**: http://localhost:8000/api/v1/redoc/

### Características de la Documentación

- ✅ Autenticación JWT integrada
- ✅ Ejemplos de requests/responses
- ✅ Pruebas en tiempo real
- ✅ Esquemas de datos detallados

## 🔧 Configuración de Producción

### Variables de Entorno

```bash
export DEBUG=False
export SECRET_KEY=tu_clave_secreta_segura
export ALLOWED_HOSTS=tu-dominio.com,127.0.0.1
export DATABASE_URL=postgresql://user:pass@localhost/db
```

### Configuraciones de Seguridad

- Configurar `ALLOWED_HOSTS` apropiadamente
- Usar `DEBUG=False`
- Configurar HTTPS
- Configurar CORS apropiadamente
- Usar base de datos segura

## 🚀 Despliegue

### Con Docker Compose

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: efc_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit los cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Para soporte técnico contactar a: support@aduanasoft.com.mx

## 📝 Changelog

### v2.0.0
- ✅ Migración completa a Django REST Framework
- ✅ Sistema de autenticación JWT
- ✅ API RESTful completa
- ✅ Sistema de logging avanzado
- ✅ Documentación automática
- ✅ Soporte multi-organización

---

**Desarrollado con ❤️ para el comercio exterior mexicano**
