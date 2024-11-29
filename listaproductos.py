# listaproductos.py -- Listado de productos a comprar

import flet as ft
from conector_bbdd import conexion_bbdd

def productListView(page: ft.Page):
    # Conexión a la base de datos
    db_connection = conexion_bbdd()
    if db_connection is None:
        return ft.Text("Error al conectar con la base de datos", color="red")
    cursor = db_connection.cursor()

    # Contenedor dinámico para el contenido principal
    dynamic_content = ft.Container(expand=True)

    # Función para cargar categorías desde la base de datos
    def load_categories():
        cursor.execute("SELECT category_icon, category_name, category_id FROM categories")
        categories = cursor.fetchall()

        options = [
            ft.dropdown.Option(
                key="*",
                text="Todos"
            )
        ]

        # Añadir el resto de las categorías
        options.extend([ 
            ft.dropdown.Option(
                key=cat[1],  
                text=f"{cat[0]} {cat[1]}"  
            )
            for cat in categories
        ])

        return options

    # Función para cargar productos desde la base de datos
    def load_products(search_query="", category_filter="*", order_by="ASC", product_type="*", min_quantity_greater=False, zero_quantity=False, product_favourite=False):
        query = """
        SELECT product_id, product_name, category_name, category_id, product_type, product_q_now, product_q_min
        FROM products
        WHERE product_name LIKE %s
        """
        
        # Añadir filtros adicionales
        params = [f"%{search_query.strip()}%"]
        
        if category_filter != "*":
            query += " AND category_name = %s"
            params.append(category_filter)
        
        if product_type != "*":
            query += " AND product_type = %s"
            params.append(product_type)
        
        if min_quantity_greater:
            query += " AND product_q_min > product_q_now"  
        
        if zero_quantity:
            query += " AND product_q_now = 0"
        
        if product_favourite:
            query += " AND product_favourite = 1" 
        
        query += " ORDER BY product_name {order}".format(order=order_by)

        try:
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al cargar productos: {e}")
            return []  
    
    
    # Definir el diálogo global
    confirmation_dialog = ft.AlertDialog(
        #title=ft.Text("Confirmación"),
        content=ft.Text("Producto añadido al carrito."),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: close_dialog())
        ],
    )

    # Función para cerrar el diálogo
    def close_dialog():
        confirmation_dialog.open = False  
        page.update()  

    # Función para añadir un producto al carrito
    def add_to_cart(product_id, category_id):
        try:
            cursor.execute("SELECT 1 FROM cart WHERE product_id = %s", (product_id,))
            existing_product = cursor.fetchone()

            if existing_product:
                confirmation_dialog.content.value = "Este producto ya está en tu carrito."
            else:
                cursor.execute("INSERT INTO cart (product_id, category_id) VALUES (%s, %s)", (product_id,category_id,))
                db_connection.commit()

                confirmation_dialog.content.value = "Producto añadido al carrito."
            

            if confirmation_dialog not in page.controls:
                page.add(confirmation_dialog)  

            confirmation_dialog.open = True  
            page.update()  

        except Exception as e:
            confirmation_dialog.content.value = f"Error al añadir producto al carrito: {e}"

            if confirmation_dialog not in page.controls:
                page.add(confirmation_dialog)

            confirmation_dialog.open = True  
            page.update() 



    # Función para refrescar la lista de productos
    def refresh_product_list():
        products = load_products(
            search_box.value, 
            category_dropdown.value, 
            order_by.value, 
            product_type_dropdown.value, 
            no_quantity_min.value, 
            no_stock.value,
            product_favourite_checkbox.value  
        )
        product_list.controls.clear()

        if products:
            for product_id, name, category_name, category_id, ptype, quantity, min_quantity in products:
                cursor.execute("SELECT category_icon FROM categories WHERE category_id = %s", (category_id,))
                category_icon = cursor.fetchone()
                category_display = f"{category_icon[0]} {category_name}" if category_icon else category_name

                product_list.controls.append(
                    ft.Card(
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(name, weight="bold", size=16),
                                        ft.Row(
                                            [
                                                ft.Text(category_display, size=14),
                                                ft.Text(f"Cantidad: {quantity}", size=12), 
                                            ]
                                        )
                                    ],
                                    alignment="start",
                                    spacing=5
                                ),
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.icons.DELETE,
                                            tooltip="Eliminar",
                                            on_click=lambda e, pid=product_id: delete_product(pid),
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.EDIT,
                                            tooltip="Editar",
                                            on_click=lambda e, pid=product_id, cid=category_id: page.edit_product_from_menu(pid, cid),
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.ADD_SHOPPING_CART,
                                            tooltip="Añadir al carrito",
                                            on_click=lambda e, pid=product_id, cid=category_id: add_to_cart(pid,cid),
                                        ),
                                    ],
                                    alignment="end",
                                    spacing=10
                                ),
                            ],
                            alignment="spaceBetween",
                            spacing=10,
                        ),
                        elevation=5,
                        margin=ft.margin.all(10)
                    )
                )
        else:
            product_list.controls.append(ft.Text("No se encontraron productos."))

        page.update()

    # Función para eliminar producto
    def delete_product(product_id):
        try:
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
            db_connection.commit()
            refresh_product_list() 
        except Exception as err:
            snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar producto: {err}"), bgcolor="red")
            
            page.add(snack_bar)
            
            snack_bar.open = True
            
            page.update()


   # Componentes del formulario de búsqueda y filtros
    search_box = ft.TextField(
        hint_text="Buscar por nombre...",
        width=150,  
        text_size=14, 
        on_change=lambda e: refresh_product_list(),
    )

    category_dropdown = ft.Dropdown(
        label="Filtrar por categoría",
        options=load_categories(),
        on_change=lambda e: refresh_product_list(),
        value="*",  
        width=150,  
        text_size=14,  
    )

    order_by = ft.Dropdown(
        label="Ordenar por",
        options=[ 
            ft.dropdown.Option(key="ASC", text="Nombre (A-Z)"),
            ft.dropdown.Option(key="DESC", text="Nombre (Z-A)"),
        ],
        value="ASC",
        on_change=lambda e: refresh_product_list(),
        width=120,  
        text_size=14,  
    )

    # Filtro por tipo de producto (Ocasionales / Básicos)
    product_type_dropdown = ft.Dropdown(
        label="Tipo de Producto",
        options=[ 
            ft.dropdown.Option(key="*", text="Todos"),
            ft.dropdown.Option(key="ocasional", text="Ocasional"),
            ft.dropdown.Option(key="básico", text="Básico"),
        ],
        on_change=lambda e: refresh_product_list(),
        value="*",
        width=150,  
        text_size=14, 
    )

    # Filtro por cantidad mínima mayor que cantidad actual
    no_quantity_min = ft.Checkbox(
        label="Reponer",
        on_change=lambda e: refresh_product_list(),
        width=120,  
    )

    # Filtro por productos con cantidad actual igual a 0
    no_stock = ft.Checkbox(
        label="Sin Stock",
        on_change=lambda e: refresh_product_list(),
        width=120, 
    )

    # Filtro por productos favoritos
    product_favourite_checkbox = ft.Checkbox(
        label="Favoritos",
        on_change=lambda e: refresh_product_list(),
        width=120,  
    )

    # Lista de productos 
    product_list = ft.ListView(
        expand=True,       
        height=400,       
    )

    # Botón de Burger para ocultar/mostrar filtros
    burger_filters = ft.IconButton(
        icon=ft.icons.MENU,
        tooltip="Ocultar/Mostrar filtros",
        on_click=lambda e: toggle_filters_visibility(),
    )

    # Función para alternar la visibilidad de los filtros
    def toggle_filters_visibility():
        if filter_column.visible:
            filter_column.visible = False
            burger_filters.icon = ft.icons.MENU
        else:
            filter_column.visible = True
            burger_filters.icon = ft.icons.CLOSE
        page.update()

    # Fila de filtros con visibilidad controlada
    filter_column = ft.Column(
        [
            ft.Row(
                [
                    category_dropdown,
                    product_type_dropdown,
                ],
                spacing=3,
                alignment="start",
            ),
            ft.Row(
                [
                    no_quantity_min,
                    no_stock,
                    product_favourite_checkbox,  
                ],
                spacing=1,
                alignment="start",
            ),
        ],
        spacing=10,
        alignment="start",
        visible=False,
    )

    # Botón de Burger para ocultar/mostrar busqueda y orden
    burger_search = ft.IconButton(
        icon=ft.icons.MENU,
        tooltip="Ocultar/Mostrar Buscador y Orden",
        on_click=lambda e: toggle_search_visibility(),
    )

    # Función para alternar la visibilidad de la busqueda y orden
    def toggle_search_visibility():
        if search_row.visible:
            search_row.visible = False
            burger_search.icon = ft.icons.MENU
        else:
            search_row.visible = True
            burger_search.icon = ft.icons.CLOSE
        page.update()

    # Fila de busqueda con visibilidad controlada
    search_row = ft.Row(
        [
            search_box,
            order_by,
        ],
        spacing=10,
        alignment="start",
        visible=False,  
    )

    # Agregar el listado al contenedor dinámico inicialmente
    dynamic_content.content = ft.Column(
        [
            ft.Text(value="Listado de Productos", size=20, weight="bold"),
            ft.Row(
                [
                    burger_search,
                    ft.Text("Buscar/Ordenar", size=18, weight="bold", color="blue"),
                    burger_filters,
                    ft.Text("Filtros", size=18, weight="bold", color="blue"),
                ],
                alignment="start",
                spacing=5,
            ),
            search_row,
            filter_column,

            ft.Divider(),
            product_list,
        ],
        alignment="start",
        horizontal_alignment="start",
        expand=True,
    )

    # Layout principal
    layout = ft.Column(
        [
            dynamic_content,  
        ],
        alignment="start",
        horizontal_alignment="start",
        expand=True,
    )

    # Cargar productos al iniciar
    refresh_product_list()

    return layout
