import flet as ft
import os  # Importar el módulo os para trabajar con variables de entorno
from home import home_main  # Cambié el nombre de la importación de `main` a `home_main`

# Obtener la contraseña desde la variable de entorno
PASSWORD = os.getenv("APP_PASSWORD_DOV", "defaultPassword")  # "defaultPassword" es el valor por defecto si no está configurada la variable

def main(page: ft.Page):
    page.title = "Aplicación Protegida"

    # Función de autenticación
    def verificar_password(e):
        if password_input.value == PASSWORD:
            page.controls.clear()  # Limpiar la página para iniciar con el contenido de home
            home_main(page)  # Llamar a la función main de home.py para cargar la vista principal
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

    # Mostrar el formulario de login en la página inicial
    page.add(login_form)

# Ejecutar el servidor web
ft.app(target=main)
