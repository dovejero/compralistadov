# home.py -- Archivo principal en el cual cargan los componentes

import flet as ft
from categorias import categoryView
from establecimientos import storeView
from productos import productView
from listaproductos import productListView
from cesta import cartView
from tickets import ticketView
from graficas import chartView

def home_main(page: ft.Page):
    page.title = "<Compra Lista>"
    page.scroll = "adaptive"
    page.theme_mode = ft.ThemeMode.LIGHT

    # Configurar el tamaño de la ventana
    page.window.width = 650  
    page.window.height = 768  

    # Contenedor para el contenido dinámico
    content_container = ft.Column()

    # Función para cambiar el contenido principal
    def show_component(component, selected_tab_index=None):
        content_container.controls.clear()
        content_container.controls.append(component)
        page.update()

        # Solo cambiar de pestaña si se pasa el índice de la pestaña seleccionada
        if selected_tab_index is not None:
            tabs.selected_index = selected_tab_index 
            page.update()

    # Función para abrir la vista de edición desde cualquier componente
    def edit_product_from_menu(product_id, category_id):
        from productos import productView  
        show_component(productView(page, product_id, category_id), selected_tab_index=3)

    # Exponer la función a otras vistas
    page.edit_product_from_menu = edit_product_from_menu

    # Función para manejar el cambio de pestaña
    def on_tab_change(e):
        if e.control.selected_index == 0:
            show_component(chartView(page), selected_tab_index=0)
        elif e.control.selected_index == 1:
            show_component(productListView(page))
        elif e.control.selected_index == 2:
            show_component(cartView(page))
        elif e.control.selected_index == 3:
            show_component(ticketView(page))  
        elif e.control.selected_index == 4:
            show_component(productView(page))  
        elif e.control.selected_index == 5:
            show_component(categoryView(page))
        elif e.control.selected_index == 6:
            show_component(storeView(page))

    # Barra de navegación con Tabs
    tabs = ft.Tabs(
        selected_index=0,  
        tabs=[
            ft.Tab(text="Estadísticas"),
            ft.Tab(text="Lista Productos"),
            ft.Tab(text="Cesta"),
            ft.Tab(text="Tickets"),
            ft.Tab(text="Productos"),
            ft.Tab(text="Categorías"),
            ft.Tab(text="Establecimientos"),
        ],
        expand=True, 
        on_change=on_tab_change 
    )

    # Layout principal
    layout = ft.Column(
        [
            tabs,  
            ft.Divider(thickness=1, height=5), 
            ft.Container(content_container, expand=True, padding=10), 
        ],
        expand=True,
    )

    # Mostrar Categorías al iniciar
    show_component(chartView(page))

    # Añadir el layout al 'page'
    page.add(layout)

ft.app(target=home_main)
