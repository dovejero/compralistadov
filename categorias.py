# categorias.py -- Archivo de crud de categorías

import flet as ft
from conector_bbdd import conexion_bbdd

def categoryView(page: ft.Page):
    # Conexión a la base de datos
    db_connection = conexion_bbdd()
    if db_connection is None:
        return ft.Text("Error al conectar con la base de datos", color="red")
    cursor = db_connection.cursor()

    # Función para agregar una categoría en la bbdd
    def add_category(e):
        name = cat_name.value.strip()
        icon = cat_icon.value

        if not name or not icon:
            message.value = "Por favor, completa todos los campos."
            page.update()
            return

        try:
            cursor.execute(
                "INSERT INTO categories (category_name, category_icon) VALUES (%s, %s)", (name, icon)
            )
            db_connection.commit()
            add_category_view(cursor.lastrowid, name, icon)
            cat_name.value = ""
            cat_icon.value = None
            message.value = ""
        except Exception as err:
            message.value = f"Error: {err}"
        finally:
            page.update()

    # Función para eliminar una categoría en la bbdd
    def delete_category(cat_id):
        try:
            cursor.execute("DELETE FROM categories WHERE category_id = %s", (cat_id,))
            db_connection.commit()
            category_list.controls.clear()
            load_categories()
        except Exception as err:
            message.value = f"Error: {err}"
        finally:
            page.update()

    # Función para editar una categoría en la bbdd
    def edit_category(cat_id):
        try:
            cursor.execute("SELECT category_name, category_icon FROM categories WHERE category_id = %s", (cat_id,))
            category_name, category_icon = cursor.fetchone()
            cat_name.value = category_name
            cat_icon.value = category_icon
            submit_button.text = "Actualizar"
            submit_button.on_click = lambda e: update_category(cat_id)
        except Exception as err:
            message.value = f"Error: {err}"
        finally:
            page.update()

    # Función para actualizar una categoría
    def update_category(cat_id):
        name = cat_name.value.strip()
        icon = cat_icon.value

        if not name or not icon:
            message.value = "Por favor, completa todos los campos."
            page.update()
            return

        try:
            cursor.execute(
                "UPDATE categories SET category_name = %s, category_icon = %s WHERE category_id = %s",
                (name, icon, cat_id),
            )
            db_connection.commit()
            category_list.controls.clear()
            load_categories()
            cat_name.value = ""
            cat_icon.value = None
            submit_button.text = "Guardar Categoría"
            submit_button.on_click = add_category
            message.value = ""
        except Exception as err:
            message.value = f"Error: {err}"
        finally:
            page.update()

    # Componentes del formulario
    cat_name = ft.TextField(
        label="Categoría",
        hint_text="Introduce el nombre de la categoría",
        width=150,
        text_size=12,
    )

    cat_icon = ft.Dropdown(
        label="Selecciona un ícono",
        hint_text="Elige un ícono",
        options=[
            ft.dropdown.Option(key="🍎", text="🍎 Fruta"),
            ft.dropdown.Option(key="🥛", text="🥛 Leche"),
            ft.dropdown.Option(key="🍞", text="🍞 Pan"),
            ft.dropdown.Option(key="🥩", text="🥩 Carne"),
            ft.dropdown.Option(key="🐟", text="🐟 Pescado"),
            ft.dropdown.Option(key="🥦", text="🥦 Verduras"),
            ft.dropdown.Option(key="🥐", text="🥐 Bollería"),
            ft.dropdown.Option(key="🧀", text="🧀 Quesos"),
            ft.dropdown.Option(key="🥜", text="🥜 Frutos Secos"),
            ft.dropdown.Option(key="🧃", text="🧃 Zumos"),
            ft.dropdown.Option(key="🫘", text="🫘 Legumbres"),
            ft.dropdown.Option(key="🍷", text="🍷 B.Alcohólicas"),
            ft.dropdown.Option(key="🦪", text="🦪 Marisco"),
            ft.dropdown.Option(key="🍝", text="🍝 Pasta"),
            ft.dropdown.Option(key="🍮", text="🍮 Lacteos"),
            ft.dropdown.Option(key="🥚", text="🥚 Huevos"),
            ft.dropdown.Option(key="🍕", text="🍕 P.Preparados"),
            ft.dropdown.Option(key="🥫", text="🥫 Conservas"),
            ft.dropdown.Option(key="🍫", text="🍫 Dulces"),
            ft.dropdown.Option(key="🫖", text="🫖 Infusiones"),
            ft.dropdown.Option(key="🧴", text="🧴 Limpieza"),
            ft.dropdown.Option(key="🧻", text="🧻 Baño"),
            ft.dropdown.Option(key="💁🏾‍♀️", text="💁🏾‍♀️ Otros"),     
        ],
        width=150,
        text_size=12,
    )

    submit_button = ft.ElevatedButton(text="Guardar Categoría", on_click=add_category, width=200)

    message = ft.Text(value="", color="red", size=12)

    # Lista de categorías
    category_list = ft.ListView(expand=True, spacing=10, height=400)

    # Función con la Query para listar las categorías
    def load_categories():
        cursor.execute("SELECT category_id, category_name, category_icon FROM categories")
        for cat_id, name, icon in cursor.fetchall():
            add_category_view(cat_id, name, icon)

    # Función para visualizar las categorías en el front
    def add_category_view(cat_id, name, icon):
        category_list.controls.append(
            ft.Card(
                content=ft.Row(
                    [
                        ft.Row(
                            [
                                ft.Text(f"{icon} {name}", size=12, weight="bold"),
                            ],
                            spacing=5
                        ),                        
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    tooltip="Editar",
                                    on_click=lambda e, id=cat_id: edit_category(id),
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    tooltip="Eliminar",
                                    on_click=lambda e, id=cat_id: delete_category(id),
                                ),
                            ],
                        ),
                    ],
                    alignment="spaceBetween", 
                    spacing=2,
                ),
                elevation=5,
                margin=ft.margin.all(10),
            )
        )

    # Layout principal
    layout = ft.Column(
        [
            ft.Text(value="Categorías", size=20, weight="bold"),
            ft.Row(
                [
                    cat_name,
                    cat_icon,
                ],
                wrap=True,
                spacing=10,
                alignment="center",
            ),
            submit_button,
            message,
            ft.Divider(),
            ft.Text(value="Listado de Categorías", size=20, weight="bold"),
            category_list,
        ],
        spacing=2,
        expand=True,
    )

    # Cargar categorías al iniciar
    load_categories()

    return layout
