# Sistema de gestión documental

Aplicación web en Flask para que instituciones educativas organicen y consulten su documentación histórica. Permite registrar documentos con metadatos, almacenar archivos, filtrar búsquedas y consultar reportes anuales.

## Requisitos

- Python 3.10+
- Dependencias listadas en `requirements.txt`

## Configuración

1. Crear y activar un entorno virtual.
2. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Inicializar la base de datos y ejecutar el servidor:

   ```bash
   flask --app app run --debug
   ```

   El proyecto crea un archivo SQLite en `instance/documents.db` y guarda los archivos subidos en `uploads/`.

## Funcionalidades

- Registro de documentos con nombre, descripción, categoría, fecha y archivo adjunto.
- Búsqueda con filtros por texto, categoría y año.
- Descarga directa de los archivos almacenados.
- Reportes anuales con totales y desglose por categoría.

## Estructura

```
app/
├── __init__.py
├── models.py
├── routes.py
├── static/
│   └── styles.css
└── templates/
    ├── base.html
    ├── index.html
    └── reports.html
```

Los archivos subidos se almacenan en `uploads/` y pueden gestionarse con copias de respaldo según las políticas institucionales.
