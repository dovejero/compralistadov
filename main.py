import flet as ft
import os  
#from home import home_main 

# Obtener la contraseña desde la variable de entorno
PASSWORD = os.getenv("APP_PASSWORD_DOV", "defaultPassword")

def main(page: ft.Page):
    print("La aplicación está arrancando...")  
    page.title = "Aplicación Protegida"

    # Función de autenticación
    def verificar_password(e):
        print("Verificando la contraseña...") 
        if password_input.value == PASSWORD:
            print("Contraseña correcta, cargando el contenido de la aplicación...")
            page.controls.clear()
            ft.TextField(password=True, hint_text="Entramos en la página")
            #home_main(page)  
            page.update() 
        else:
            error_message.value = "Contraseña incorrecta"
            page.update()  

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
    page.update()  

# Ejecutar el servidor web
ft.app(target=main)
