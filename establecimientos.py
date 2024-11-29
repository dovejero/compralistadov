# establecimientos.py -- Archivo de crud de establecimientos

import flet as ft
from conector_bbdd import conexion_bbdd

def storeView(page: ft.Page):
    # Conexión a la base de datos
    db_connection = conexion_bbdd()
    if db_connection is None:
        return ft.Text("Error al conectar con la base de datos", color="red")
    cursor = db_connection.cursor()

    # Función para agregar un establecimiento en la bbdd
    def add_store(e):
        s_name = store_name.value.strip()
        if not s_name:
            message.value = "Por favor, completa todos los campos."
            page.update()
            return
        try:
            cursor.execute("INSERT INTO stores (store_name) VALUES (%s)", (s_name,))
            db_connection.commit()
            add_store_view(s_name)
            store_name.value = ""
            message.value = ""
        except Exception as err:
            message.value = f"Error: {err}"
        finally:
            page.update()

    # Función para eliminar un establecimiento en la bbdd
    def delete_store(s_name):
        try:
            cursor.execute("DELETE FROM stores WHERE store_name = %s", (s_name,))
            db_connection.commit()
            store_list.controls.clear()
            store_stores()
        except Exception as err:
            message.value = f"Error: {err}"
        finally:
            page.update()

    # Función para editar un establecimiento en la bbdd
    def edit_store(s_name):
        try:
            cursor.execute("SELECT store_name FROM stores WHERE store_name = %s", (s_name,))
            (name,) = cursor.fetchone()
            store_name.value = name
            submit_button.text = "Actualizar"
            submit_button.on_click = lambda e: update_store(s_name)
        except Exception as err:
            message.value = f"Error: {err}"
        finally:
            page.update()

    # Función para actualizar un establecimiento
    def update_store(s_name):
        name = store_name.value.strip()
        if not name:
            message.value = "Por favor, completa todos los campos."
            page.update()
            return
        try:
            cursor.execute(
                "UPDATE stores SET store_name = %s WHERE store_name = %s", (name, s_name)
            )
            db_connection.commit()
            store_list.controls.clear()
            store_stores()
            store_name.value = ""
            submit_button.text = "Guardar Establecimiento"
            submit_button.on_click = add_store
            message.value = ""
        except Exception as err:
            message.value = f"Error: {err}"
        finally:
            page.update()

    # Componentes del formulario
    store_name = ft.TextField(
        label="Nombre del Establecimiento",
        hint_text="Introduce el nombre del Establecimiento",
        width=250, 
        text_size=14,
    )

    submit_button = ft.ElevatedButton(
        text="Guardar Establecimiento", on_click=add_store, width=200
    )

    message = ft.Text(value="", color="red", size=12)

    # Lista de establecimientos
    store_list = ft.ListView(expand=True, spacing=10, height=400)

    # Función con la Query para listar los establecimientos
    def store_stores():
        cursor.execute("SELECT store_name FROM stores")
        for (s_name,) in cursor.fetchall():
            add_store_view(s_name)

    # Función para visualizar los establecimientos en el front
    def add_store_view(s_name):
        store_list.controls.append(
            ft.Card(
                content=ft.Row(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.icons.STORE_MALL_DIRECTORY, size=12),
                                ft.Text(s_name, size=12, weight="bold", expand=True),
                            ],
                            alignment="start",
                        ),
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    tooltip="Editar",
                                    on_click=lambda e, name=s_name: edit_store(name),
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    tooltip="Eliminar",
                                    on_click=lambda e, name=s_name: delete_store(name),
                                ),
                            ],
                            alignment="end",
                        ),
                    ],
                    alignment="spaceBetween",
                    spacing=2,
                ),
                elevation=5,
                margin=ft.margin.all(10),
            )
        )
        page.update()

    # Layout principal
    layout = ft.Column(
        [
            ft.Text(value="Establecimientos", size=20, weight="bold"),
            ft.Row(
                [
                    store_name,
                ],
                wrap=True,
                spacing=10,
                alignment="center",
            ),
            submit_button,
            message,
            ft.Divider(),
            ft.Text(value="Listado de establecimientos", size=20, weight="bold"),
            store_list,
        ],
        spacing=10,
        expand=True,
    )

    # Cargar establecimientos al iniciar
    store_stores()

    return layout
