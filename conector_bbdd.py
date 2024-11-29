# conector_bbdd.py -- Archivo de conexión con la bbdd

import mysql.connector
from mysql.connector import Error

def conexion_bbdd():
    # Datos de conexión
    host = "junction.proxy.rlwy.net"  # Host público proporcionado por Railway
    user = "root"  # Usuario
    password = "jURqPxcdhqWnqOWNMfdIniecgMyYYUdh"  # Contraseña
    database = "railway"  # Nombre de la base de datos
    port = 24540  # Puerto externo para conexiones públicas

    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )

        if conn.is_connected():
            print("Conexión ok")
            return conn  # Retornamos la conexión activa
    except Error as e:
        print(f"Error de conexión: {e}")
        return None  # Retornamos None si falla la conexión

