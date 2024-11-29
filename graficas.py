# graficas.py -- Archivo gráficas datos compras

import flet as ft
from conector_bbdd import conexion_bbdd

def chartView(page: ft.Page):
    # Lista para los controles del gráfico y mensaje
    chart_list = ft.Row(expand=True, spacing=20)

    # Mensaje para errores o notificaciones
    message = ft.Text(value="", color="red", size=12)

    def badge(icon, size):
        return ft.Container(
            ft.Text(" " + icon, size=size / 2),
            width=size,
            height=size,
            border=ft.border.all(1, ft.colors.WHITE),
            border_radius=size / 2,
            bgcolor=ft.colors.BLACK,
        )

    # Función para obtener los datos de gasto por categoría del mes actual
    def obtener_gastos_por_categoria():
        cursor = None  
        db_connection = None  
        try:
            # Conexión a la base de datos
            db_connection = conexion_bbdd()
            if db_connection is None:
                raise Exception("Error al conectar con la base de datos")

            cursor = db_connection.cursor() 

            # Consulta SQL para obtener el total de gasto por categoría en el mes actual
            cursor.execute("""
                SELECT cat.category_icon, cat.category_name, SUM(t.ticket_product_quantity * t.ticket_product_price) AS total_gasto
                FROM ticket t
                JOIN categories cat ON t.category_id = cat.category_id
                WHERE DATE_FORMAT(t.ticket_date, '%Y-%m') = DATE_FORMAT(NOW(), '%Y-%m')
                GROUP BY cat.category_name;
            """)

            # Obtener los resultados de la consulta
            datos = cursor.fetchall()

            # Si no hay datos, retornar categorías con total 0
            if not datos:
                return [], [], []

            # Separar los datos de categorías y totales
            cat_icon = [fila[0] for fila in datos]
            categorias = [fila[1] for fila in datos]
            totales = [fila[2] if fila[2] is not None else 0 for fila in datos]

            return categorias, totales, cat_icon

        except Exception as e:
            print(f"Error al obtener los datos: {e}")
            return [], [], []

        finally:
            if cursor:
                cursor.close()  
            if db_connection:
                db_connection.close() 

    # Cargar los datos y preparar el gráfico
    def load_chart():
        categorias, totales, cat_icon = obtener_gastos_por_categoria()

        if not categorias or not totales:
            message.value = "No hay datos disponibles para este mes."
            page.update()
            return

        total_gasto = sum(totales)
        porcentajes = [(total / total_gasto) * 100 if total_gasto > 0 else 0 for total in totales]

        # Encontramos el índice del valor con el mayor porcentaje
        max_index = porcentajes.index(max(porcentajes))

        # Crear los segmentos del PieChart
        sections = []
        for i in range(len(categorias)):
            color = ft.colors.GREEN if i == max_index else ft.colors.BLUE  # El mayor porcentaje tiene un color diferente
            # Validamos que tanto categoria como porcentaje sean correctos antes de agregarla
            if categorias[i] and porcentajes[i] is not None:
                sections.append(
                    ft.PieChartSection(
                        porcentajes[i],
                        title=f"{porcentajes[i]:.2f}%",
                        title_style=ft.TextStyle(size=12, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                        color=color,
                        radius=50,  # Hacemos el gráfico más pequeño
                        badge=badge(cat_icon[i], 30),
                        badge_position=0.98,
                    ),
                )

        # Si no se crearon secciones para el gráfico, mostrar un mensaje de error
        if not sections:
            message.value = "No se pudieron generar secciones para el gráfico."
            page.update()
            return

        pie_chart = ft.PieChart(
            sections=sections,
            sections_space=2,
            center_space_radius=40,
        )

        # Crear la lista de gastos por categoría
        gasto_por_categoria = []
        for i in range(len(categorias)):
            gasto_por_categoria.append(
                ft.Row(
                    [
                        badge(cat_icon[i], 30), 
                        ft.Text(categorias[i], size=12),  
                        ft.Text(f"€ {totales[i]:.2f}", size=12), 
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                )
            )

        gasto_column = ft.Column(
            [
                ft.Text("Info detallada:", size=16, weight="bold"),
                *gasto_por_categoria, 
                ft.Divider(),  
                ft.Text(f"Total gasto: € {total_gasto:.2f}", size=14, weight="bold"),
            ],
            spacing=5,
            expand=True,
        )

        # Añadir PieChart y mensaje en una columna
        chart_column = ft.Column(
            [
                ft.Text(value="Gastos mensuales por Categoría", size=14),
                message,
                pie_chart,
            ],
            spacing=10,
            expand=True,
        )

        # Agregar las dos columnas (gráfico y listado) en una fila
        chart_list.controls.append(
            ft.Row(
                [chart_column, gasto_column],
                expand=True,
                spacing=20,
            )
        )

        page.update()

    # Llamamos a la función para cargar los datos y preparar el gráfico
    load_chart()

    # Layout principal
    layout = ft.Column(
        [
            ft.Text(value="Análisis de Gastos", size=20, weight="bold"),
            chart_list, 
        ],
        spacing=10,
        expand=True,
    )

    return layout
