import flet as ft
from home import home_main

PASSWORD = "proyectoDAM"

def main(page: ft.Page):
    page.title = "Aplicación Protegida"

    # Función de autenticación
    def verificar_password(e):
        if password_input.value == PASSWORD:
            page.clean()  # Limpia la página
            home_main(page)  # Llama nuevamente a la función principal para mostrar el contenido
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
