# tickets.py -- Archivo listado tickets generados compras

import flet as ft
from conector_bbdd import conexion_bbdd

def ticketView(page: ft.Page):
    # Lista de tickets agrupados por ticket_cart_id
    ticket_list = ft.ListView(expand=True, spacing=10, height=400)

    # Mensaje para errores o notificaciones
    message = ft.Text(value="", color="red", size=12)

    # Dropdown para seleccionar el filtro
    filter_dropdown = ft.Dropdown(
        label="Ordenar por",
        options=[
            ft.dropdown.Option("Fecha"),
            ft.dropdown.Option("Establecimiento"), 
        ],
        value="Fecha", 
        on_change=lambda e: load_tickets(), 
        width=200, 
    )

    # Alinear el Dropdown a la derecha
    filter_dropdown_container = ft.Row(
        [filter_dropdown],
        alignment="start", 
        expand=True,
    )

    # Función para cargar los tickets agrupados con el filtro seleccionado
    def load_tickets():
        try:
            # Conexión a la base de datos
            db_connection = conexion_bbdd()
            if db_connection is None:
                message.value = "Error al conectar con la base de datos"
                page.update()
                return

            cursor = db_connection.cursor()

            selected_filter = filter_dropdown.value

            if selected_filter == "Establecimiento":
                query = """
                    SELECT 
                        ticket_cart_id,
                        MIN(ticket_date) AS ticket_date,
                        MIN(store_name) AS store_name,
                        COUNT(*) AS product_count,
                        SUM(ticket_product_quantity * ticket_product_price) AS total_price
                    FROM ticket
                    GROUP BY ticket_cart_id, store_name
                    ORDER BY store_name, ticket_date ASC
                """
            else:
                query = """
                    SELECT 
                        ticket_cart_id,
                        MIN(ticket_date) AS ticket_date,
                        MIN(store_name) AS store_name,
                        COUNT(*) AS product_count,
                        SUM(ticket_product_quantity * ticket_product_price) AS total_price
                    FROM ticket
                    GROUP BY ticket_cart_id, ticket_date
                    ORDER BY ticket_date ASC
                """

            cursor.execute(query)
            tickets = cursor.fetchall()

            ticket_list.controls.clear()

            for ticket_cart_id, ticket_date, store_name, product_count, total_price in tickets:
                add_ticket_view(ticket_cart_id, ticket_date, store_name, product_count, total_price)

        except Exception as e:
            message.value = f"Error al cargar los tickets: {e}"
        finally:
            # Cerrar la conexión y cursor al final
            if cursor:
                cursor.close()
            if db_connection:
                db_connection.close()
            page.update()

    # Función para mostrar cada ticket en la lista
    def add_ticket_view(ticket_cart_id, ticket_date, store_name, product_count, total_price):
        ticket_list.controls.append(
            ft.Card(
                content=ft.Row(
                    [
                        # Información del ticket alineada horizontalmente
                        ft.Row(
                            [
                                ft.Text(f" {ticket_date}", size=12, weight="bold"),
                                ft.Text(f" | {store_name}", size=12),
                                ft.Text(f" | {product_count}", size=12),
                                ft.Text(f" | Total: {total_price:.2f}€", size=12, color="green"),
                            ],
                            spacing=5,
                        ),
                        # Botón "Ver detalles"
                        ft.IconButton(
                            icon=ft.icons.PREVIEW, 
                            tooltip="Comprar", 
                            on_click=lambda e, id=ticket_cart_id: show_ticket_details(id),
                        ),
                    ],
                    alignment="spaceBetween",
                    spacing=2,
                ),
                elevation=5,
                margin=ft.margin.all(10),
            )
        )

    # Función para mostrar los detalles de un ticket en un alert
    def show_ticket_details(ticket_cart_id):
        try:
            db_connection = conexion_bbdd()
            if db_connection is None:
                raise Exception("No se pudo conectar a la base de datos")
            cursor = db_connection.cursor()

            cursor.execute("""
                SELECT 
                    t.product_id,
                    p.product_name,
                    t.ticket_product_quantity,
                    t.ticket_product_price,
                    (t.ticket_product_quantity * t.ticket_product_price) AS line_total
                FROM ticket t
                JOIN products p ON t.product_id = p.product_id
                WHERE t.ticket_cart_id = %s
            """, (ticket_cart_id,))
            ticket_details = cursor.fetchall()

            # Crear un GridView para mostrar los detalles en columnas
            details_grid = ft.Column(
                [

                    ft.Row(
                        [
                            ft.Text("Producto", weight="bold", size=12, expand=2),
                            ft.Text("Cantidad", weight="bold", size=12, expand=1),
                            ft.Text("Precio Unitario", weight="bold", size=12, expand=1),
                            ft.Text("Total Producto", weight="bold", size=12, expand=1),
                        ],
                        spacing=10,
                    ),
                    ft.Divider(height=1),

                    *[
                        ft.Row(
                            [
                                ft.Text(product_name, weight="bold", size=12, expand=2),
                                ft.Text(f"{quantity}", size=12, expand=1),
                                ft.Text(f"{price:.2f}€", size=12, expand=1),
                                ft.Text(f"{line_total:.2f}€", size=12, expand=1),
                            ],
                            spacing=10,
                        )
                        for _, product_name, quantity, price, line_total in ticket_details
                    ],
                    ft.Divider(height=1),

                    ft.Row(
                        [
                            ft.Text("", expand=2),  
                            ft.Text("", expand=1),
                            ft.Text("Total del Ticket:", weight="bold", size=12, expand=1),
                            ft.Text(
                                f"{sum(line_total for _, _, _, _, line_total in ticket_details):.2f}€",
                                weight="bold",
                                size=12,
                                expand=1,
                                color="green",
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                spacing=5,
            )

            def close_dialog():
                page.dialog.open = False
                page.update()

            # Mostrar alerta con los detalles
            page.dialog = ft.AlertDialog(
                title=ft.Text("Info Ticket"),
                content=details_grid,
                actions=[
                    ft.TextButton("Cerrar", on_click=lambda e: close_dialog()),
                ],
                actions_alignment="end",
            )
            page.dialog.open = True
            page.update()

        except Exception as e:
            message.value = f"Error al mostrar los detalles: {e}"
            page.update()
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db_connection' in locals():
                db_connection.close()

    # Layout principal
    layout = ft.Column(
        [
            ft.Text(value="Tickets", size=20, weight="bold"),
            message,
            filter_dropdown_container,  
            ticket_list,
        ],
        spacing=10,
        expand=True,
    )

    # Cargar tickets al iniciar
    load_tickets()

    return layout
