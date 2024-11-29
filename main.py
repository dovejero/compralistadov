import flet as ft
import os  # Importar el módulo os para trabajar con variables de entorno
from home import main

# Obtener la contraseña desde la variable de entorno
PASSWORD = os.getenv("APP_PASSWORD_DOV", "defaultPassword")  # "defaultPassword" es el valor por defecto si no está configurada la variable

def main(page: ft.Page):
    page.title = "Aplicación Protegida"

    # Función de autenticación
    def verificar_password(e):
        if password_input.value == PASSWORD:
            login_form.visible = False  # Ocultar el formulario de login
            page.update()  # Actualizar la página para reflejar el cambio de visibilidad
            page.add(main_content)  # Mostrar el contenido principal
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

    # Contenido principal que se muestra después del login (puedes modificar este contenido)
    main_content = ft.Column([
        ft.Text("Contenido de la aplicación", size=24),
        # Aquí puedes agregar más controles que quieras mostrar después de la autenticación
    ])

    # Añadir el formulario de login a la página al inicio
    page.add(login_form)

# Ejecutar el servidor web sin especificar `view`
ft.app(target=main)
