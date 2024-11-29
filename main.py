import flet as ft
import os  # Importar el módulo os para trabajar con variables de entorno
from home import main

# Obtener la contraseña desde la variable de entorno
PASSWORD = os.getenv("APP_PASSWORD_DOV", "defaultPassword")  # "defaultPassword" es el valor por defecto si no está configurada la variable
PRUEBA = os.getenv("APP_PRUEBA_DOV", "defaultPassword")

print("Contraseña desde la variable de entorno:", PRUEBA)
 
def main(page: ft.Page):
    page.title = "Aplicación Protegida"

    # Función de autenticación
    def verificar_password(e):
        if password_input.value == PASSWORD:
            page.clean()  # Limpia la página
            main(page)  # Llama nuevamente a la función principal para mostrar el contenido
        else:
            error_message.value = "Contraseña incorrecta"
            page.update()

    # Elementos de la pantalla de login
    password_input = ft.TextField(password=True, hint_text="Introduce la contraseña")
    error_message = ft.Text(value="", color="red")
    login_button = ft.ElevatedButton(text="Acceder", on_click=verificar_password)

    # Añadir los controles a la pantalla inicial
    page.add(
        ft.Column(
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
    )

# Ejecutar el servidor web sin especificar `view`
ft.app(target=main)
