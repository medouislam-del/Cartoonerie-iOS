import sqlite3
import re
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.core.window import Window

# FIX: Keyboard behavior for Android
Window.softinput_mode = 'below_target'

DB_NAME = "products.db"

def init_db():
    """Initialise la base de données au démarrage."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (code TEXT PRIMARY KEY, name TEXT, format TEXT)''')
    conn.commit()
    conn.close()

class SearchScreen(Screen):
    search_mode = StringProperty('code')
    result_text = StringProperty('')

    def do_search(self):
        input_text = self.ids.input_search.text.strip()
        if not input_text:
            self.result_text = "[color=ff3333]Veuillez entrer un terme.[/color]"
            return

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        rows = []

        try:
            if self.search_mode == 'code':
                c.execute("SELECT * FROM products WHERE code LIKE ?", (f'%{input_text}%',))
                rows = c.fetchall()
            elif self.search_mode == 'name':
                c.execute("SELECT * FROM products WHERE name LIKE ?", (f'%{input_text}%',))
                rows = c.fetchall()
            elif self.search_mode == 'format':
                c.execute("SELECT * FROM products")
                all_rows = c.fetchall()
                for row in all_rows:
                    fmt = str(row[2]).strip().replace(" ", "").lower()
                    match = re.match(r"(\d+)[x×*]", fmt)
                    if match and match.group(1) == input_text:
                        rows.append(row)
        except Exception as e:
            self.result_text = f"[color=ff3333]Erreur: {str(e)}[/color]"
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
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM products ORDER BY name ASC")
        rows = c.fetchall()
        conn.close()
        for code, name, fmt in rows:
            self.ids.product_list.add_widget(
                Label(text=f"{code} | {fmt} | {name}", size_hint_y=None, height='40dp', markup=True)
            )

class EditProductScreen(Screen):
    def clear_inputs(self):
        self.ids.input_code.text = ""
        self.ids.input_name.text = ""
        self.ids.input_format.text = ""

    def add_product(self):
        code, name, fmt = self.ids.input_code.text.strip(), self.ids.input_name.text.strip(), self.ids.input_format.text.strip()
        if not all([code, name, fmt]): return
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT INTO products VALUES (?, ?, ?)", (code, name, fmt))
            conn.commit()
            conn.close()
            self.clear_inputs()
        except sqlite3.IntegrityError:
            pass

    def update_product(self):
        code, name, fmt = self.ids.input_code.text.strip(), self.ids.input_name.text.strip(), self.ids.input_format.text.strip()
        if not code: return
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE products SET name=?, format=? WHERE code=?", (name, fmt, code))
        conn.commit()
        conn.close()

    def delete_product(self):
        code = self.ids.input_code.text.strip()
        if not code: return
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM products WHERE code=?", (code,))
        conn.commit()
        conn.close()
        self.clear_inputs()

class ProductApp(App):
    def build(self):
        init_db()
        return Builder.load_string(KV)

KV = """
ScreenManager:
    SearchScreen:
    EditProductScreen:
    ProductListScreen:

<SearchScreen>:
    name: 'search'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        Image:
            source: 'logo.jpg'
            size_hint_y: None
            height: '150dp'
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
            hint_text: 'Entrer code, laize ou nom...'
            size_hint_y: None
            height: '40dp'
            multiline: False
        BoxLayout:
            size_hint_y: None
            height: '45dp'
            spacing: 10
            Button:
                text: 'Rechercher'
                background_color: 0.2, 0.6, 1, 1
                on_press: root.do_search()
            Button:
                text: 'Gérer un produit'
                on_press: app.root.current = 'edit'
        ScrollView:
            Label:
                id: lbl_result
                text: root.result_text
                markup: True
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None

<EditProductScreen>:
    name: 'edit'
    ScrollView:
        do_scroll_x: False
        BoxLayout:
            orientation: 'vertical'
            padding: 20
            spacing: 15
            size_hint_y: None
            height: self.minimum_height
            Label:
                text: '[b]Gestion du Stock[/b]'
                markup: True
                size_hint_y: None
                height: '40dp'
            TextInput:
                id: input_code
                hint_text: 'Code (Unique)'
                size_hint_y: None
                height: '45dp'
                multiline: False
            TextInput:
                id: input_name
                hint_text: 'Nom du Produit'
                size_hint_y: None
                height: '45dp'
                multiline: False
            TextInput:
                id: input_format
                hint_text: 'Format (ex: 472X1166X122)'
                size_hint_y: None
                height: '45dp'
                multiline: False
            BoxLayout:
                size_hint_y: None
                height: '45dp'
                spacing: 10
                Button:
                    text: 'Ajouter'
                    on_press: root.add_product()
                Button:
                    text: 'Modifier'
                    on_press: root.update_product()
            Button:
                text: 'Supprimer'
                size_hint_y: None
                height: '45dp'
                background_color: 1, 0.3, 0.3, 1
                on_press: root.delete_product()
            Button:
                text: 'Voir la liste complète'
                size_hint_y: None
                height: '45dp'
                on_press: app.root.current = 'list'
            Button:
                text: '⬅ Retour à la recherche'
                size_hint_y: None
                height: '45dp'
                on_press: app.root.current = 'search'

<ProductListScreen>:
    name: 'list'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        Label:
            text: '[b]Tous les Produits[/b]'
            markup: True
            size_hint_y: None
            height: '40dp'
        ScrollView:
            GridLayout:
                id: product_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                row_default_height: '40dp'
                spacing: 5
        Button:
            text: '⬅ Retour à la gestion'
            size_hint_y: None
            height: '50dp'
            on_press: app.root.current = 'edit'
"""

if __name__ == '__main__':
    ProductApp().run()
