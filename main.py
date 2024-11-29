import flet as ft
import os  # Importar el módulo os para trabajar con variables de entorno
from home import home_main  # Asegurémonos de importar la función correcta

# Obtener la contraseña desde la variable de entorno
PASSWORD = os.getenv("APP_PASSWORD_DOV", "defaultPassword")  # "defaultPassword" es el valor por defecto si no está configurada la variable

def main(page: ft.Page):
    print("La aplicación está arrancando...")  # Mensaje de depuración para ver si la función main se ejecuta
    page.title = "Aplicación Protegida"

    # Función de autenticación
    def verificar_password(e):
        print("Verificando la contraseña...")  # Mensaje para saber si estamos dentro de la función de verificación
        if password_input.value == PASSWORD:
            print("Contraseña correcta, cargando el contenido de la aplicación...")
            page.controls.clear()  # Limpiar la página para asegurar que no haya conflictos de contenido
            home_main(page)  # Cargar la vista principal de home.py
            page.update()  # Actualizar la página después de cargar el contenido
        else:
            error_message.value = "Contraseña incorrecta"
            page.update()  # Actualizar la página con el mensaje de error

    # Elementos de la pantalla de login
    password_input = ft.TextField(password=True, hint_text="Introduce la contraseña")
    error_message = ft.Text(value="", color="red")
    login_button = ft.ElevatedButton(text="Acceder", on_click=verificar_password)

    # Contenedor para el formulario de login
    login_form = ft.Column(
        [
            ft.Text("Acceso Restringido", size=24, weight="bold"),
            password_input,
            error_message,
            login_button,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
    )

    # Añadir el formulario de login a la página al inicio
    page.add(login_form)
    page.update()  # Asegurarse de que la página se actualiza con el formulario

# Ejecutar el servidor web
ft.app(target=main)
