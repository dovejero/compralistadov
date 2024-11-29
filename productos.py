# productos.py -- CRUD de alta de productos

import flet as ft
from conector_bbdd import conexion_bbdd

def productView(page: ft.Page, product_id: str = None, category_id: int = None):
    # Conexión a la base de datos
    db_connection = conexion_bbdd()
    if db_connection is None:
        return ft.Text("Error al conectar con la base de datos", color="red")
    cursor = db_connection.cursor()

    # Obtener categorías con sus iconos (tabla categories)
    def load_categories():
        cursor.execute("SELECT category_id, category_name, category_icon FROM categories")
        categories = cursor.fetchall()
        return [
            ft.dropdown.Option(
                key=str(cat_id),  
                text=cat_name  
            )
            for cat_id, cat_name, cat_icon in categories
        ]

    # Preparación de datos del producto
    if product_id:
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        if not product:
            return ft.Text("Producto no encontrado", color="red")
        product_name = product[3]
        category_id = category_id
        product_info = product[4]
        product_type = product[5]
        quantity_now = product[7]
        quantity_min = product[6]
        product_price_value = float(product[8]) if product[8] else 0.0
        product_favourite = product[9] 
    else:
        product_name = ""
        category_id = ""
        product_info = ""
        product_type = "basico"
        quantity_now = ""
        quantity_min = ""
        product_price_value = 0.0
        product_favourite = 0 

    product_price = ft.Text(
        value=f"{product_price_value:.2f} €",
        color="grey",
        size=14,
        weight="bold",
    )

    # Guardar Producto
    def save_product(e):
        try:
            category_id = int(category_dropdown.value)
            category_name = next(
                (opt.text for opt in category_dropdown.options if opt.key == str(category_id)),
                None
            )
        except (ValueError, TypeError):
            message.value = "Selecciona una categoría válida."
            page.update()
            return

        name = product_name_field.value.strip()
        description = product_info_field.value.strip()
        product_type = product_type_group.value
        q_now = quantity_now_field.value
        q_min = quantity_min_field.value

        if not (category_id and name and description and (q_now or product_type == "Ocasional")):
            message.value = "Por favor, completa todos los campos requeridos."
            page.update()
            return

        try:
            if product_id:
                cursor.execute(
                    """
                    UPDATE products
                    SET category_id = %s, category_name = %s, product_name = %s,
                        product_description = %s, product_type = %s, product_q_min = %s,
                        product_q_now = %s, product_favourite = %s
                    WHERE product_id = %s
                    """,
                    (category_id, category_name, name, description, product_type, q_min, q_now, product_favourite, product_id),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO products (category_id, category_name, product_name,
                                          product_description, product_type, product_q_min,
                                          product_q_now, product_price, product_favourite)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 0.0, %s)
                    """,
                    (category_id, category_name, name, description, product_type, q_min, q_now, product_favourite),
                )
            db_connection.commit()
            message.value = "Producto guardado correctamente."
            message.color = "green"
            
            category_dropdown.value = None
            product_name_field.value = ""
            product_info_field.value = ""
            product_type_group.value = "basico"
            quantity_now_field.value = ""
            quantity_min_field.value = ""
            page.update()

        except Exception as err:
            message.value = f"Error: {err}"
            message.color = "red"
            page.update()

    # Función para true o false en favorito 
    def toggle_product_favourite(e):
        nonlocal product_favourite  
        product_favourite = 1 if product_favourite == 0 else 0  
        product_favourite_icon.icon = ft.icons.FAVORITE if product_favourite == 1 else ft.icons.FAVORITE_BORDER  
        page.update()

    # Formulario
    category_dropdown = ft.Dropdown(
        label="Categoría",
        hint_text="Categoría",
        options=load_categories(),
        value=str(category_id) if category_id else None,
        width=200,
        text_size=12,
        #height=40,  
    )
    product_name_field = ft.TextField(
        label="Nombre del Producto",
        hint_text="Nombre del producto",
        width=200,
        text_size=12,
        value=product_name,
        height=40,  
    )
    product_info_field = ft.TextField(
        label="Descripción",
        multiline=True,
        max_lines=3,
        hint_text="Describe el producto",
        width=420,
        text_size=12,
        value=product_info, 
    )
    product_type_group = ft.RadioGroup(
        content=ft.Column(
            [
                ft.Container(ft.Radio(label="Básico", value="basico")),
                ft.Container(ft.Radio(label="Ocasional", value="ocasional")),
            ],
            spacing=10,
        ),
        value=product_type,
    )
    quantity_now_field = ft.TextField(
        label="Cantidad Actual",
        hint_text="Introduce la cantidad actual",
        width=100,
        text_size=12,
        value=str(quantity_now),
        height=40, 
    )
    quantity_min_field = ft.TextField(
        label="Cantidad Mínima",
        hint_text="Introduce la cantidad mínima",
        width=100,
        text_size=12,
        value=str(quantity_min),
        height=40,  
    )

    # Botón de favorito con el icono que cambia al pulsar
    product_favourite_icon = ft.IconButton(
        icon=ft.icons.FAVORITE_BORDER if product_favourite == 0 else ft.icons.FAVORITE,
        on_click=toggle_product_favourite,  
    )

    submit_button = ft.ElevatedButton("Guardar Producto", on_click=save_product)
    message = ft.Text(value="", color="red", size=12)

    # Layout principal 
    layout = ft.Column(
        [
            ft.Text(value="Añadir Producto", size=20, weight="bold"),
            ft.Row(
                [
                    ft.Column([category_dropdown, product_name_field]),
                    ft.Column([product_type_group], spacing=10)
                ],
                spacing=5,
                alignment="start",
            ),
            product_info_field,
            ft.Row([quantity_now_field, quantity_min_field, product_favourite_icon, ft.Text(value="Favorito", size=15)], spacing=10),
            submit_button,
            message,
        ],
        alignment="start",
        spacing=10,
    )

    return layout
