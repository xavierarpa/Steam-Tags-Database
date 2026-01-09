"""
Script para exportar la base de datos SQLite a formato CSV
"""

import sqlite3
import csv
import argparse
import os


def export_to_csv(database_path, output_path, table_name="games_filter"):
    """
    Exporta una tabla de la base de datos SQLite a un archivo CSV.
    
    Parameters:
        database_path: Ruta al archivo de base de datos SQLite
        output_path: Ruta donde guardar el archivo CSV
        table_name: Nombre de la tabla a exportar (por defecto: games_filter)
    """
    if not os.path.exists(database_path):
        print(f"Error: No se encontró la base de datos en '{database_path}'")
        print("Ejecuta primero 'python game_database.py' para crear la base de datos.")
        return False
    
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Verificar que la tabla existe y obtener el nombre validado
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        result = cursor.fetchone()
        if not result:
            print(f"Error: La tabla '{table_name}' no existe en la base de datos.")
            conn.close()
            return False
        
        # Usar el nombre de tabla validado de sqlite_master para evitar SQL injection
        validated_table_name = result[0]
        
        # Obtener todos los datos
        cursor.execute(f"SELECT * FROM [{validated_table_name}]")
        rows = cursor.fetchall()
        
        # Obtener nombres de columnas
        column_names = [description[0] for description in cursor.description]
        
        # Escribir a CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(column_names)  # Encabezados
            writer.writerows(rows)  # Datos
        
        conn.close()
        
        print(f"Exportación completada exitosamente!")
        print(f"Archivo guardado en: {os.path.abspath(output_path)}")
        print(f"Total de juegos exportados: {len(rows)}")
        return True
        
    except sqlite3.Error as e:
        print(f"Error de base de datos: {e}")
        return False
    except IOError as e:
        print(f"Error al escribir el archivo: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Exporta la base de datos de Steam Tags a CSV'
    )
    parser.add_argument(
        '--database', '-d',
        default='tags_database.db',
        help='Ruta al archivo de base de datos SQLite (por defecto: tags_database.db)'
    )
    parser.add_argument(
        '--output', '-o',
        default='games_export.csv',
        help='Ruta donde guardar el archivo CSV (por defecto: games_export.csv)'
    )
    parser.add_argument(
        '--table', '-t',
        default='games_filter',
        help='Nombre de la tabla a exportar (por defecto: games_filter)'
    )
    
    args = parser.parse_args()
    
    # Expandir ~ para rutas de usuario (ej: ~/Desktop)
    output_path = os.path.expanduser(args.output)
    
    export_to_csv(args.database, output_path, args.table)


if __name__ == "__main__":
    main()
