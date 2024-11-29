import flet as ft

def main(page: ft.Page):
    page.title = "Bienvenido a la Aplicación"
    page.scroll = "adaptive"
    page.theme_mode = ft.ThemeMode.DARK

    # Configurar la ventana
    page.window.width = 650
    page.window.height = 768

    # Mostrar contenido principal
    content = ft.Column([ft.Text("Contenido de la aplicación", size=24)])

    # Añadir el contenido principal a la página
    page.add(content)
    page.update()  # Asegurarse de que la página se actualiza con el contenido

ft.app(target=main)