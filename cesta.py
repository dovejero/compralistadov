import flet as ft
from conector_bbdd import conexion_bbdd
from datetime import datetime, timedelta

def cartView(page: ft.Page):
    # Conexión a la base de datos
    db_connection = conexion_bbdd()
    if db_connection is None:
        return ft.Text("Error al conectar con la base de datos", color="red")
    cursor = db_connection.cursor()

    # Lista para mostrar los productos en el carrito
    cart_list = ft.ListView(expand=True, spacing=10, height=400)

    # Campo Text para "Precio provisional"
    provisional_price_text = ft.Text(value="Subtotal: 0.00€", size=14, weight="bold")

    # Dropdown para establecimientos
    store_dropdown = ft.Dropdown(
        width=180,
        label="Establecimiento",
        options=[]
    )

    # Campo mensaje
    message = ft.Text(value="", color="red", size=12)

    # Cargar los establecimientos
    def load_stores():
        try:
            cursor.execute("SELECT store_name, store_name FROM stores")
            stores = cursor.fetchall()
            store_dropdown.options = [ft.dropdown.Option(store_name) for _, store_name in stores]
        except Exception as e:
            message.value = f"Error al cargar los establecimientos: {e}"
        page.update()

    # Función para calcular el precio provisional
    def calculate_provisional_price():
        total_price = 0
        cursor.execute(""" 
            SELECT c.cart_quantity, c.cart_price, c.cart_selected 
            FROM cart c 
        """)
        for cart_quantity, cart_price, cart_selected in cursor.fetchall():
            if cart_selected == 1:  # Solo sumar los productos seleccionados
                total_price += cart_quantity * cart_price
        provisional_price_text.value = f"Subtotal: {total_price:.2f}€"
        page.update()

    # Función para cargar los productos del carrito
    def load_cart():
        cursor.execute("""
            SELECT c.cart_id, c.product_id, c.category_id, c.cart_quantity, c.cart_price, c.cart_selected, 
                p.product_name, cat.category_icon
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            JOIN categories cat ON c.category_id = cat.category_id
        """)
        for cart_id, product_id, category_id, cart_quantity, cart_price, cart_selected, product_name, category_icon in cursor.fetchall():
            add_cart_item_view(cart_id, product_id, category_id, product_name, cart_quantity, cart_price, cart_selected, category_icon)

        # Calcular el precio provisional después de cargar todos los productos
        calculate_provisional_price()

    # Función para actualizar la cantidad, precio y el estado de selección en la base de datos
    def update_cart_item(cart_id, quantity, price, selected):
        try:
            cursor.execute("""
                UPDATE cart
                SET cart_quantity = %s, cart_price = %s, cart_selected = %s
                WHERE cart_id = %s
            """, (quantity, price, selected, cart_id))
            db_connection.commit()
            message.value = "Carrito actualizado correctamente."
            calculate_provisional_price()  # Recalcular el precio provisional
        except Exception as e:
            message.value = f"Error al actualizar el carrito: {e}"
        finally:
            page.update()

    # Función para eliminar un producto del carrito
    def delete_cart_item(cart_id):
        try:
            cursor.execute("DELETE FROM cart WHERE cart_id = %s", (cart_id,))
            db_connection.commit()
            cart_list.controls.clear()
            load_cart() 
        except Exception as e:
            message.value = f"Error al eliminar el producto del carrito: {e}"
        finally:
            page.update()

    # Función para mostrar la alerta con detalles del producto
    def show_product_details(product_id):
        cursor.execute("""
            SELECT p.product_name, p.product_price, p.product_q_min, p.product_q_now, p.product_description
            FROM products p
            WHERE p.product_id = %s
        """, (product_id,))
        product = cursor.fetchone()
        
        if product:
            product_name, product_price, product_q_min, product_q_now, product_description = product
            
            def close_dialog():
                page.dialog.open = False
                page.update()
           
            # Crear el AlertDialog con los detalles
            alert_dialog = ft.AlertDialog(
                title=ft.Text(f"{product_name}"),
                content=ft.Column(
                    [
                        ft.Text(f"Descripción: {product_description}", size=14),
                        ft.Text(f"Precio: {product_price:.2f}€", size=14),
                        ft.Text(f"Unidades actuales: {product_q_now}", size=14),
                        ft.Text(f"Unidades mínimas: {product_q_min}", size=14),
                    ],
                ),
                actions=[ft.TextButton("Cerrar", on_click=lambda e: close_dialog())]
            )
            page.dialog = alert_dialog
            alert_dialog.open = True
            page.update()

    # Función para agregar un producto al carrito (vista individual)
    def add_cart_item_view(cart_id, product_id, category_id, product_name, cart_quantity, cart_price, cart_selected, category_icon):
        quantity_field = ft.TextField(
            value=str(cart_quantity),
            width=50,
            height=50,
            text_size=16,
            on_blur=lambda e, id=cart_id: update_cart(id, e.control.value, price_field.value, checkbox.value)
        )

        price_field = ft.TextField(
            value=str(cart_price),
            width=60,
            height=50,
            text_size=16,
            on_blur=lambda e, id=cart_id: update_cart(id, quantity_field.value, e.control.value, checkbox.value)
        )

        checkbox = ft.Checkbox(value=bool(cart_selected), on_change=lambda e, id=cart_id: update_cart(id, quantity_field.value, price_field.value, e.control.value))

        # Botón de información
        info_button = ft.IconButton(
            icon=ft.icons.INFO_ROUNDED, 
            tooltip="Ver detalles", 
            on_click=lambda e, id=product_id: show_product_details(id)
        )

        cart_list.controls.append(
            ft.Card(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Row([ft.Text(category_icon), ft.Text(product_name, size=14, weight="bold", expand=True), info_button,                         ft.IconButton(icon=ft.icons.REMOVE_SHOPPING_CART_ROUNDED, tooltip="Eliminar", on_click=lambda e, id=cart_id: delete_cart_item(id))]),
                                ft.Row([ft.Row([quantity_field, ft.Text("unds")]), ft.Row([price_field, ft.Text("€")]), ft.Row([ft.Text(""), checkbox])]),
                            ],
                            alignment="start",
                            spacing=5,
                        ),
                    ],
                    alignment="start",
                    spacing=10,
                    expand=True,
                ),
                elevation=5,
                margin=ft.margin.all(10),
            )
        )

    def update_cart(cart_id, quantity, price, selected):
        try:
            price = float(price)
            if price <= 0:
                message.value = "El precio no puede ser 0 o negativo."
                page.update()
                return  
            update_cart_item(cart_id, int(quantity), price, selected)
        except ValueError:
            message.value = "Por favor, ingresa valores válidos para cantidad y precio."
        finally:
            page.update()

    def process_purchase():
        try:
            # Verificar si se ha seleccionado un establecimiento
            selected_store = store_dropdown.value
            if not selected_store:
                message.value = "Seleccione un establecimiento antes de continuar."
                page.update()
                return

            # Obtener los productos seleccionados del carrito
            cursor.execute("""
                SELECT c.product_id, c.cart_quantity, c.cart_price
                FROM cart c
                WHERE c.cart_selected = TRUE
            """)
            selected_products = cursor.fetchall()

            # Verificar si hay productos seleccionados
            if not selected_products:
                message.value = "No hay productos seleccionados para comprar."
                page.update()
                return

            # Verificar si algún producto tiene precio 0 o cantidad menor a 1
            for _, cart_quantity, cart_price in selected_products:
                if cart_price <= 0:
                    message.value = "El precio de los productos debe ser mayor que 0."
                    page.update()
                    return
                if cart_quantity < 1:
                    message.value = "La cantidad de productos seleccionados debe ser al menos 1."
                    page.update()
                    return

            # Generar un ticket_cart_id único
            cursor.execute("SELECT IFNULL(MAX(ticket_cart_id), 0) + 1 FROM ticket")
            ticket_cart_id = cursor.fetchone()[0]

            # Fecha de compra
            ticket_date = datetime.now().strftime('%Y-%m-%d')

            # Insertar cada producto en la tabla ticket
            for product_id, cart_quantity, cart_price in selected_products:
                # Obtener el category_id del producto
                cursor.execute("SELECT category_id FROM products WHERE product_id = %s", (product_id,))
                category_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO ticket (ticket_cart_id, product_id, ticket_product_quantity, ticket_product_price, store_name, ticket_date, category_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (ticket_cart_id, product_id, cart_quantity, cart_price, selected_store, ticket_date, category_id))

                # Actualizar el precio y la cantidad actual del producto en la tabla products
                cursor.execute("""
                    UPDATE products
                    SET product_price = %s, product_q_now = product_q_now + %s
                    WHERE product_id = %s
                """, (cart_price, cart_quantity, product_id))

            # Eliminar los productos seleccionados de la tabla cart
            cursor.execute("DELETE FROM cart WHERE cart_selected = TRUE")
            db_connection.commit()

            # Mensaje de éxito
            message.value = f"Compra realizada con éxito. ID del ticket: {ticket_cart_id}"
            cart_list.controls.clear()  
            load_cart()  
        except Exception as e:
            db_connection.rollback()
            message.value = f"Error al procesar la compra: {e}"
        finally:
            page.update()

    layout = ft.Column(
        [
            ft.Text(value="Cesta", size=20, weight="bold"),
            ft.Row(
                [
                    store_dropdown,  
                    provisional_price_text, 
                    ft.IconButton(icon=ft.icons.LOCAL_GROCERY_STORE_ROUNDED, tooltip="Comprar", on_click=lambda e: process_purchase()),
                ],
                alignment="spaceBetween",
                spacing=10,
            ),
            message,
            cart_list,
        ],
        spacing=2,
        expand=True,
    )

    load_stores()  
    load_cart()  

    return layout
