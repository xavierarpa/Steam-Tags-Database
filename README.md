# Steam Tags Database

Base de datos de juegos de Steam con sus etiquetas (tags). Este proyecto extrae información de la tienda de Steam y la almacena en una base de datos SQLite local.

## Requisitos Previos

- Python 3.6 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/xavierarpa/Steam-Tags-Database.git
   cd Steam-Tags-Database
   ```

2. **Instala las dependencias:**

   ```bash
   pip install requests beautifulsoup4 steamapi
   ```

## Uso Local

### Crear/Actualizar la Base de Datos

Ejecuta el script principal para crear o actualizar la base de datos de juegos:

```bash
python game_database.py
```

> **Nota:** Este proceso puede tomar bastante tiempo ya que necesita recorrer todas las páginas de la tienda de Steam.

La base de datos se guardará como `tags_database.db` en el directorio actual.

### Exportar a CSV

Para exportar la base de datos a formato CSV (que puedes abrir en Excel o guardar en tu Escritorio), ejecuta:

```bash
python export_to_csv.py
```

Esto creará un archivo `games_export.csv` que puedes copiar a tu Escritorio o cualquier otra ubicación.

#### Exportar directamente al Escritorio

En **Windows**:
```bash
python export_to_csv.py --output "%USERPROFILE%\Desktop\games_export.csv"
```

En **macOS/Linux**:
```bash
python export_to_csv.py --output ~/Desktop/games_export.csv
```

## Estructura de la Base de Datos

La tabla `games_filter` contiene:

| Campo   | Tipo   | Descripción                          |
|---------|--------|--------------------------------------|
| id      | TEXT   | ID único del juego en Steam          |
| title   | TEXT   | Nombre del juego                     |
| tags    | TEXT   | Etiquetas del juego separadas por coma |

## Ejemplo de Datos Exportados

```csv
id,title,tags
730,Counter-Strike 2,"FPS,Shooter,Multiplayer,Competitive,Action"
570,Dota 2,"Free to Play,MOBA,Multiplayer,Strategy,Team-Based"
```

## Archivos del Proyecto

- `game_database.py` - Script principal que crea y mantiene la base de datos
- `export_to_csv.py` - Script para exportar la base de datos a CSV
- `database_tests.py` - Tests del proyecto

## Licencia

Este proyecto es de código abierto.
