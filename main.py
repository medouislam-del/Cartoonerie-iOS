import sqlite3
import re
import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivy.utils import platform

# Keeps the keyboard from covering your text inputs
Window.softinput_mode = 'below_target'

class ProductApp(App):
    def build(self):
        # Point to your existing database file
        self.db_path = os.path.join(os.path.dirname(__file__), "products.db")
        return Builder.load_string(KV)

class SearchScreen(Screen):
    search_mode = StringProperty('code')
    result_text = StringProperty('')

    def do_search(self):
        input_text = self.ids.input_search.text.strip()
        if not input_text:
            self.result_text = "[color=ff3333]Veuillez entrer un terme.[/color]"
            return

        app = App.get_running_app()
        conn = sqlite3.connect(app.db_path)
        c = conn.cursor()
        rows = []

        try:
            if self.search_mode == 'code':
                c.execute("SELECT * FROM products WHERE code LIKE ?", (f'%{input_text}%',))
            elif self.search_mode == 'name':
                c.execute("SELECT * FROM products WHERE name LIKE ?", (f'%{input_text}%',))
            elif self.search_mode == 'format':
                c.execute("SELECT * FROM products")
                all_rows = c.fetchall()
                for row in all_rows:
                    fmt = str(row[2]).strip().replace(" ", "").lower()
                    match = re.match(r"(\d+)[x×*]", fmt)
                    if match and match.group(1) == input_text:
                        rows.append(row)
                rows = rows if self.search_mode == 'format' else c.fetchall()
            
            if self.search_mode != 'format':
                rows = c.fetchall()
        except:
            pass
        finally:
            conn.close()

        if rows:
            self.result_text = ''
            for code, name, fmt in rows:
                self.result_text += f"[b]Produit:[/b] {name}\nCode: {code} | Format: {fmt}\n\n"
        else:
            self.result_text = "[color=ff3333]Aucun produit trouvé.[/color]"

class ProductListScreen(Screen):
    def on_pre_enter(self):
        self.update_product_list()

    def update_product_list(self):
        self.ids.product_list.clear_widgets()
        app = App.get_running_app()
        conn = sqlite3.connect(app.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM products ORDER BY name ASC")
        rows = c.fetchall()
        conn.close()
        for code, name, fmt in rows:
            self.ids.product_list.add_widget(
                Label(text=f"{code} | {fmt} | {name}", size_hint_y=None, height='40dp', markup=True)
            )

class EditProductScreen(Screen):
    # (Existing Add/Update/Delete methods remain the same)
    def add_product(self):
        pass # Add your existing logic here

KV = """
ScreenManager:
    SearchScreen:
    EditProductScreen:
    ProductListScreen:

<SearchScreen>:
    name: 'search'
    BoxLayout:
        orientation: 'vertical'
        # NOTCH FIX: Top padding set to 50dp
        padding: [20, 50, 20, 10]
        spacing: 10
        Image:
            source: 'logo.jpg'
            size_hint_y: None
            height: '140dp'
            allow_stretch: True
        Label:
            text: '[b]Generale Cartoonerie Produits[/b]'
            markup: True
            font_size: '18sp'
            size_hint_y: None
            height: '40dp'
        BoxLayout:
            size_hint_y: None
            height: '40dp'
            ToggleButton:
                text: 'Par Code'
                group: 'search_mode'
                state: 'down'
                on_press: root.search_mode = 'code'
            ToggleButton:
                text: 'Par Laize'
                group: 'search_mode'
                on_press: root.search_mode = 'format'
            ToggleButton:
                text: 'Par Nom'
                group: 'search_mode'
                on_press: root.search_mode = 'name'
        TextInput:
            id: input_search
            hint_text: 'Entrer code...'
            size_hint_y: None
            height: '45dp'
            multiline: False
        Button:
            text: 'Rechercher'
            size_hint_y: None
            height: '45dp'
            background_color: 0.2, 0.6, 1, 1
            on_press: root.do_search()
        ScrollView:
            Label:
                id: lbl_result
                text: root.result_text
                markup: True
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
"""

if __name__ == '__main__':
    ProductApp().run()
