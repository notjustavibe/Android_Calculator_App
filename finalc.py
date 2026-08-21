import math
from datetime import datetime
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.metrics import dp

# ---------------------------------------------------------------- palette --
BG_COLOR = (0.93, 0.93, 0.94, 1)
CARD_COLOR = (1, 1, 1, 1)
BTN_DEFAULT = (0.90, 0.90, 0.91, 1)
BTN_DEFAULT_DOWN = (0.82, 0.82, 0.84, 1)
BTN_ACCENT = (0.98, 0.47, 0.16, 1)
BTN_ACCENT_DOWN = (1.0, 0.58, 0.28, 1)
TEXT_DARK = (0.12, 0.12, 0.14, 1)
TEXT_GRAY = (0.55, 0.55, 0.58, 1)
TEXT_WHITE = (1, 1, 1, 1)

SUPER_DIGITS = {
    "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
    "5": "5", "6": "6", "7": "7", "8": "8", "9": "9",
}
OPERATORS_CONTINUE = {"+", "-", "*", "/", "^"}

LINEAR_UNITS = {
    "Length": {
        "Meter": 1, "Kilometer": 1000, "Centimeter": 0.01, "Millimeter": 0.001,
        "Mile": 1609.344, "Yard": 0.9144, "Foot": 0.3048, "Inch": 0.0254,
    },
    "Area": {
        "Square Meter": 1, "Square Kilometer": 1e6, "Square Centimeter": 1e-4,
        "Hectare": 10000, "Acre": 4046.86, "Square Mile": 2.59e6, "Square Foot": 0.092903,
    },
    "Volume": {
        "Liter": 1, "Milliliter": 0.001, "Gallon (US)": 3.78541,
        "Quart (US)": 0.946353, "Cup": 0.24,
    },
    "Weight": {
        "Kilogram": 1, "Gram": 0.001, "Pound": 0.453592, "Ounce": 0.0283495,
        "Metric Ton": 1000,
    },
    "Speed": {
        "Meter/sec": 1, "Kilometer/hour": 0.277778, "Mile/hour": 0.44704,
        "Knot": 0.514444, "Foot/sec": 0.3048,
    },
    "Pressure": {
        "Pascal": 1, "Kilopascal": 1000, "Bar": 100000, "Atmosphere": 101325,
        "PSI": 6894.76, "mmHg": 133.322,
    },
    "Power": {
        "Watt": 1, "Kilowatt": 1000, "Horsepower": 745.7, "Megawatt": 1e6,
    },
}

# Standard text labels replacing ambiguous unicode symbols
CONVERTER_CARDS = [
    ("¥", "Currency", "stub"),
    ("L", "Length", "convert"),
    ("A", "Area", "convert"),
    ("V", "Volume", "convert"),
    ("W", "Weight", "convert"),
    ("°C", "Temperature", "convert"),
    ("S", "Speed", "convert"),
    ("P", "Pressure", "convert"),
    ("PWR", "Power", "convert"),
    ("01", "Number system", "numsys"),
]

NUM_SYSTEM_BASES = {"Binary": 2, "Octal": 8, "Decimal": 10, "Hexadecimal": 16}

# ------------------------------------------------------------- widgets ----
class CircleButton(Button):
    def __init__(self, bg_color=BTN_DEFAULT, bg_color_down=BTN_DEFAULT_DOWN,
                 text_color=TEXT_DARK, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.background_down = ""
        self.color = text_color
        self.bg_color = bg_color
        self.bg_color_down = bg_color_down
        
        with self.canvas.before:
            self.color_instruction = Color(*self.bg_color)
            self.circle = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._update_circle, size=self._update_circle)
        self.bind(state=self._update_state)

    def _update_circle(self, *args):
        side = min(self.width, self.height) * 0.84
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        self.circle.pos = (cx - side / 2, cy - side / 2)
        self.circle.size = (side, side)

    def _update_state(self, instance, value):
        self.color_instruction.rgba = (
            self.bg_color_down if value == "down" else self.bg_color
        )

    def set_active(self, active):
        self.bg_color = BTN_ACCENT if active else BTN_DEFAULT
        self.bg_color_down = BTN_ACCENT_DOWN if active else BTN_DEFAULT_DOWN
        self.color = TEXT_WHITE if active else TEXT_DARK
        self.color_instruction.rgba = self.bg_color


class IconButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.background_down = ""
        self.color = TEXT_DARK


class CardButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.background_down = ""
        self.color = TEXT_DARK
        self.halign = "center"
        self.valign = "middle"
        self.line_height = 1.3
        
        with self.canvas.before:
            self.color_instruction = Color(*CARD_COLOR)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(size=self._update_text_size)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _update_text_size(self, *args):
        self.text_size = (self.width - dp(8), self.height - dp(8))


class HistoryCard(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.background_down = ""
        self.halign = "left"
        self.valign = "middle"
        self.markup = True
        
        with self.canvas.before:
            self.color_instruction = Color(*CARD_COLOR)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(size=self._update_text_size)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _update_text_size(self, *args):
        self.text_size = (self.width - dp(24), None)


def make_top_bar(back_callback=None, title=""):
    bar = BoxLayout(size_hint=(1, None), height=dp(48), spacing=dp(4))
    if back_callback:
        back_btn = IconButton(text="<-", font_size=dp(18), size_hint=(0.15, 1))
        back_btn.bind(on_release=back_callback)
        bar.add_widget(back_btn)
    else:
        bar.add_widget(Label(size_hint=(0.15, 1)))
        
    title_label = Label(
        text=title, font_size=dp(20), color=TEXT_DARK, bold=True,
        halign="left", valign="middle", size_hint=(0.85, 1),
    )
    title_label.bind(size=lambda i, v: setattr(i, "text_size", v))
    bar.title_label = title_label
    bar.add_widget(title_label)
    return bar


# --------------------------------------------------------------- screens --
class CalcScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expression = ""
        self.display_text = ""
        self.scientific_mode = False
        self.degree_mode = True
        self.inv_mode = False
        self.superscript_active = False
        self.just_evaluated = False

        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6))
        with root.canvas.before:
            Color(*BG_COLOR)
            self.bg_rect = RoundedRectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)
        self._bg_widget = root
        self.add_widget(root)

        # Clean ASCII-compatible navigation icons
        top_bar = BoxLayout(size_hint=(1, 0.06), spacing=dp(4))
        top_bar.add_widget(IconButton(text="calc", font_size=dp(14), size_hint=(0.2, 1)))
        top_bar.add_widget(Label(size_hint=(0.35, 1)))
        
        self.sci_icon_btn = IconButton(text="fx", font_size=dp(16), size_hint=(0.15, 1))
        self.sci_icon_btn.bind(on_release=self.toggle_scientific)
        top_bar.add_widget(self.sci_icon_btn)
        
        conv_btn = IconButton(text="unit", font_size=dp(14), size_hint=(0.15, 1))
        conv_btn.bind(on_release=lambda i: self._go("converter_grid"))
        top_bar.add_widget(conv_btn)
        
        hist_btn = IconButton(text="hist", font_size=dp(14), size_hint=(0.15, 1))
        hist_btn.bind(on_release=lambda i: self._go("history"))
        top_bar.add_widget(hist_btn)
        
        root.add_widget(top_bar)

        self.history_label = Label(
            text="", font_size=dp(15), color=TEXT_GRAY,
            halign="right", valign="middle", size_hint=(1, 0.05),
        )
        self.history_label.bind(size=self._update_label_text_size)
        root.add_widget(self.history_label)

        self.display = Label(
            text="0", font_size=dp(48), color=TEXT_DARK,
            halign="right", valign="middle", size_hint=(1, 0.15), bold=True,
        )
        self.display.bind(size=self._update_label_text_size)
        root.add_widget(self.display)

        self.grid_container = BoxLayout(size_hint=(1, 0.74))
        root.add_widget(self.grid_container)
        self._build_grid()

    def _go(self, screen_name):
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction="left")
        app.root.current = screen_name

    def _update_bg(self, *args):
        self.bg_rect.pos = self._bg_widget.pos
        self.bg_rect.size = self._bg_widget.size

    def _update_label_text_size(self, instance, value):
        instance.text_size = (instance.width - dp(6), instance.height)

    def _build_grid(self):
        self.grid_container.clear_widgets()
        self._toggle_refs = {}
        
        if self.scientific_mode:
            grid = GridLayout(cols=5, spacing=dp(4))
            rows = [
                ["sin", "cos", "tan", "rad", "deg"],
                ["log", "ln", "(", ")", "inv"],
                ["!", "AC", "%", "DEL", "/"],
                ["^", "7", "8", "9", "*"],
                ["sqrt", "4", "5", "6", "-"],
                ["pi", "1", "2", "3", "+"],
                ["e", "00", "0", ".", "="],
            ]
            digit_font, fn_font = dp(20), dp(13)
        else:
            grid = GridLayout(cols=4, spacing=dp(6))
            rows = [
                ["AC", "%", "DEL", "/"],
                ["7", "8", "9", "*"],
                ["4", "5", "6", "-"],
                ["1", "2", "3", "+"],
                ["00", "0", ".", "="],
            ]
            digit_font, fn_font = dp(30), dp(18)

        for row in rows:
            for label in row:
                if label == "=":
                    btn = CircleButton(
                        text=label, bg_color=BTN_ACCENT, bg_color_down=BTN_ACCENT_DOWN,
                        text_color=TEXT_WHITE, font_size=dp(26), bold=True,
                    )
                elif label.isdigit() or label == "00":
                    btn = CircleButton(text=label, font_size=digit_font, bold=True)
                else:
                    btn = CircleButton(text=label, font_size=fn_font, bold=True)
                    
                if label == "deg":
                    self._toggle_refs["deg"] = btn
                elif label == "rad":
                    self._toggle_refs["rad"] = btn
                elif label == "inv":
                    self._toggle_refs["inv"] = btn
                    
                btn.bind(on_press=self.on_button_press)
                grid.add_widget(btn)

        self.grid_container.add_widget(grid)
        if "deg" in self._toggle_refs:
            self._toggle_refs["deg"].set_active(self.degree_mode)
            self._toggle_refs["rad"].set_active(not self.degree_mode)
            self._toggle_refs["inv"].set_active(self.inv_mode)

    def toggle_scientific(self, instance):
        self.scientific_mode = not self.scientific_mode
        self.sci_icon_btn.text = "123" if self.scientific_mode else "fx"
        self._build_grid()

    def on_button_press(self, instance):
        label = instance.text
        
        if label == "AC":
            self.expression = ""
            self.display_text = ""
            self.history_label.text = ""
            self.display.text = "0"
            self.superscript_active = False
            return
            
        # Backspace handling
        if label == "DEL":
            self.expression = self.expression[:-1]
            self.display_text = self.display_text[:-1]
            self.display.text = self.display_text or "0"
            return
            
        if label == "=":
            self._evaluate()
            return
            
        if label == "deg":
            self.degree_mode = True
            self._toggle_refs["deg"].set_active(True)
            self._toggle_refs["rad"].set_active(False)
            return
            
        if label == "rad":
            self.degree_mode = False
            self._toggle_refs["deg"].set_active(False)
            self._toggle_refs["rad"].set_active(True)
            return
            
        if label == "inv":
            self.inv_mode = not self.inv_mode
            self._toggle_refs["inv"].set_active(self.inv_mode)
            return

        if self.just_evaluated and label not in OPERATORS_CONTINUE:
            self.expression = ""
            self.display_text = ""
            self.history_label.text = ""
        self.just_evaluated = False

        if label.isdigit() or label == "00":
            digits = label
            for d in digits:
                self.expression += d
                self.display_text += d
            self.display.text = self.display_text or "0"
            return
            
        if label == ".":
            self.expression += "."
            self.display_text += "."
            self.display.text = self.display_text
            return

        self.superscript_active = False
        
        if label == "sin":
            fn = "asin(" if self.inv_mode else "sin("
            self.expression += fn
            self.display_text += ("asin(" if self.inv_mode else "sin(")
        elif label == "cos":
            fn = "acos(" if self.inv_mode else "cos("
            self.expression += fn
            self.display_text += ("acos(" if self.inv_mode else "cos(")
        elif label == "tan":
            fn = "atan(" if self.inv_mode else "tan("
            self.expression += fn
            self.display_text += ("atan(" if self.inv_mode else "tan(")
        elif label == "log":
            self.expression += "log10("
            self.display_text += "log("
        elif label == "ln":
            self.expression += "log("
            self.display_text += "ln("
        elif label == "sqrt":
            self.expression += "sqrt("
            self.display_text += "sqrt("
        elif label == "pi":
            self.expression += "pi"
            self.display_text += "pi"
        elif label == "e":
            self.expression += "e"
            self.display_text += "e"
        elif label == "^":
            self.expression += "**"
            self.display_text += "^"
        elif label == "!":
            self.expression += "factorial("
            self.display_text += "fact("
        elif label == "*":
            self.expression += "*"
            self.display_text += "*"
        elif label == "/":
            self.expression += "/"
            self.display_text += "/"
        elif label == "%":
            self.expression += "/100"
            self.display_text += "%"
        else:
            self.expression += label
            self.display_text += label
            
        self.display.text = self.display_text or "0"

    def _evaluate(self):
        if not self.expression:
            return

        # --- FIX: Auto-close unclosed parentheses ---
        open_parens = self.expression.count("(")
        close_parens = self.expression.count(")")
        if open_parens > close_parens:
            missing = ")" * (open_parens - close_parens)
            self.expression += missing
            self.display_text += missing
            self.display.text = self.display_text
        # --------------------------------------------

        deg = self.degree_mode
        safe_globals = {
            "__builtins__": {},
            "sin": lambda x: math.sin(math.radians(x)) if deg else math.sin(x),
            "cos": lambda x: math.cos(math.radians(x)) if deg else math.cos(x),
            "tan": lambda x: math.tan(math.radians(x)) if deg else math.tan(x),
            "asin": lambda x: math.degrees(math.asin(x)) if deg else math.asin(x),
            "acos": lambda x: math.degrees(math.acos(x)) if deg else math.acos(x),
            "atan": lambda x: math.degrees(math.atan(x)) if deg else math.atan(x),
            "sqrt": math.sqrt,
            "log": math.log,
            "log10": math.log10,
            "pi": math.pi,
            "e": math.e,
            "factorial": lambda x: math.factorial(int(x)),
        }
        try:
            result = eval(self.expression, safe_globals, {})
            result_str = self._format_result(result)
            App.get_running_app().add_history(self.display_text, result_str)
            self.history_label.text = self.display_text + " ="
            self.display.text = result_str
            self.expression = result_str
            self.display_text = result_str
            self.just_evaluated = True
        except ZeroDivisionError:
            self.display.text = "Cannot divide by 0"
            self.expression = ""
            self.display_text = ""
            self.just_evaluated = True
        except Exception:
            self.display.text = "Error"
            self.expression = ""
            self.display_text = ""
            self.just_evaluated = True

    @staticmethod
    def _format_result(result):
        if isinstance(result, float):
            if result.is_integer():
                return str(int(result))
            return f"{result:.10g}"
        return str(result)

    def load_value(self, text):
        self.expression = text
        self.display_text = text
        self.display.text = text
        self.just_evaluated = True


class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        with root.canvas.before:
            Color(*BG_COLOR)
            self.bg_rect = RoundedRectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)
        self._bg_widget = root
        self.add_widget(root)

        top_bar = make_top_bar(back_callback=self._back, title="History")
        trash_btn = IconButton(text="Clear", font_size=dp(14), size_hint=(0.2, 1))
        trash_btn.bind(on_release=self._clear_all)
        top_bar.add_widget(trash_btn)
        root.add_widget(top_bar)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.list_layout = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=(0, dp(8)))
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)
        root.add_widget(self.scroll)

    def _update_bg(self, *args):
        self.bg_rect.pos = self._bg_widget.pos
        self.bg_rect.size = self._bg_widget.size

    def _back(self, instance):
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction="right")
        app.root.current = "calc"

    def on_pre_enter(self, *args):
        self._refresh()

    def _refresh(self):
        self.list_layout.clear_widgets()
        app = App.get_running_app()
        if not app.history:
            self.list_layout.add_widget(
                Label(text="No history yet", color=TEXT_GRAY, size_hint_y=None, height=dp(60))
            )
            return
        for entry in reversed(app.history):
            card = HistoryCard(
                text=f"[color=888888]{entry['expr']}[/color]\n"
                     f"[b][size={int(dp(22))}]{entry['result']}[/size][/b]\n"
                     f"[color=aaaaaa][size={int(dp(12))}]{entry['date']}[/size][/color]",
                size_hint_y=None, height=dp(90),
            )
            card.bind(on_release=lambda inst, r=entry["result"]: self._reuse(r))
            self.list_layout.add_widget(card)

    def _reuse(self, result):
        app = App.get_running_app()
        app.calc_screen.load_value(result)
        self._back(None)

    def _clear_all(self, instance):
        App.get_running_app().history = []
        self._refresh()


class ConverterGridScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        with root.canvas.before:
            Color(*BG_COLOR)
            self.bg_rect = RoundedRectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)
        self._bg_widget = root
        self.add_widget(root)

        root.add_widget(make_top_bar(back_callback=self._back, title="Unit converter"))

        grid = GridLayout(cols=3, spacing=dp(10), size_hint=(1, None), padding=(0, dp(10)))
        grid.bind(minimum_height=grid.setter("height"))
        for icon, name, action in CONVERTER_CARDS:
            card = CardButton(
                text=f"{icon}\n{name}", font_size=dp(16),
                size_hint=(None, None), size=(dp(105), dp(105)),
            )
            card.bind(on_release=lambda inst, n=name, a=action: self._open(n, a))
            grid.add_widget(card)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(grid)
        root.add_widget(scroll)

    def _update_bg(self, *args):
        self.bg_rect.pos = self._bg_widget.pos
        self.bg_rect.size = self._bg_widget.size

    def _back(self, instance):
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction="right")
        app.root.current = "calc"

    def _open(self, name, action):
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction="left")
        if action == "convert":
            app.converter_detail.set_category(name)
            app.root.current = "converter_detail"
        elif action == "numsys":
            app.root.current = "number_system"
        else:
            popup = Popup(
                title=name,
                content=Label(text="This category isn't available offline yet.", color=TEXT_DARK),
                size_hint=(0.8, 0.3),
            )
            popup.open()


class ConverterDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.category = "Length"

        self.root_box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        with self.root_box.canvas.before:
            Color(*BG_COLOR)
            self.bg_rect = RoundedRectangle(pos=self.root_box.pos, size=self.root_box.size)
        self.root_box.bind(pos=self._update_bg, size=self._update_bg)
        self.add_widget(self.root_box)

        self.top_bar = make_top_bar(back_callback=self._back, title="Convert")
        self.root_box.add_widget(self.top_bar)

        units_row = BoxLayout(size_hint=(1, 0.1), spacing=dp(8))
        self.from_spinner = Spinner(text="", values=[])
        self.to_spinner = Spinner(text="", values=[])
        units_row.add_widget(self.from_spinner)
        
        swap_btn = IconButton(text="<->", font_size=dp(16), size_hint=(0.2, 1))
        swap_btn.bind(on_release=self._swap)
        units_row.add_widget(swap_btn)
        units_row.add_widget(self.to_spinner)
        self.root_box.add_widget(units_row)

        self.value_input = TextInput(
            text="1", multiline=False, input_filter="float",
            font_size=dp(24), size_hint=(1, 0.12), padding=[dp(12), dp(14)],
        )
        self.value_input.bind(text=self._on_value_change)
        self.root_box.add_widget(self.value_input)

        self.result_label = Label(
            text="", font_size=dp(26), color=TEXT_DARK, bold=True,
            size_hint=(1, 0.15),
        )
        self.root_box.add_widget(self.result_label)

        use_btn = CardButton(text="Use in calculator", font_size=dp(16), size_hint=(1, 0.1))
        use_btn.bind(on_release=self._use_result)
        self.root_box.add_widget(use_btn)

        self.root_box.add_widget(Label(size_hint=(1, 1)))

        self.from_spinner.bind(text=lambda i, v: self._recalculate())
        self.to_spinner.bind(text=lambda i, v: self._recalculate())

    def _update_bg(self, *args):
        self.bg_rect.pos = self.root_box.pos
        self.bg_rect.size = self.root_box.size

    def _back(self, instance):
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction="right")
        app.root.current = "converter_grid"

    def set_category(self, category):
        self.category = category
        self.top_bar.title_label.text = category
        if category == "Temperature":
            units = ["Celsius", "Fahrenheit", "Kelvin"]
        else:
            units = list(LINEAR_UNITS[category].keys())
        self.from_spinner.values = units
        self.to_spinner.values = units
        self.from_spinner.text = units[0]
        self.to_spinner.text = units[1] if len(units) > 1 else units[0]
        self._recalculate()

    def _swap(self, instance):
        self.from_spinner.text, self.to_spinner.text = self.to_spinner.text, self.from_spinner.text

    def _on_value_change(self, instance, value):
        self._recalculate()

    def _recalculate(self):
        try:
            val = float(self.value_input.text)
        except ValueError:
            self.result_label.text = ""
            return
        f_unit, t_unit = self.from_spinner.text, self.to_spinner.text
        if not f_unit or not t_unit:
            return
        try:
            if self.category == "Temperature":
                res = self._convert_temperature(val, f_unit, t_unit)
            else:
                factors = LINEAR_UNITS[self.category]
                res = val * factors[f_unit] / factors[t_unit]
            self.result_label.text = f"{CalcScreen._format_result(res)} {t_unit}"
        except Exception:
            self.result_label.text = "Error"

    def _use_result(self, instance):
        text = self.result_label.text.split(" ")[0]
        if text and text != "Error":
            App.get_running_app().calc_screen.load_value(text)
            app = App.get_running_app()
            app.root.transition = SlideTransition(direction="right")
            app.root.current = "calc"

    @staticmethod
    def _convert_temperature(value, from_unit, to_unit):
        if from_unit == "Celsius":
            c = value
        elif from_unit == "Fahrenheit":
            c = (value - 32) * 5 / 9
        else:
            c = value - 273.15
        if to_unit == "Celsius":
            return c
        elif to_unit == "Fahrenheit":
            return c * 9 / 5 + 32
        else:
            return c + 273.15


class NumberSystemScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        with root.canvas.before:
            Color(*BG_COLOR)
            self.bg_rect = RoundedRectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)
        self._bg_widget = root
        self.add_widget(root)

        root.add_widget(make_top_bar(back_callback=self._back, title="Number system"))

        units_row = BoxLayout(size_hint=(1, 0.1), spacing=dp(8))
        bases = list(NUM_SYSTEM_BASES.keys())
        self.from_spinner = Spinner(text="Decimal", values=bases)
        self.to_spinner = Spinner(text="Binary", values=bases)
        units_row.add_widget(self.from_spinner)
        units_row.add_widget(Label(text="->", size_hint=(0.2, 1), color=TEXT_DARK))
        units_row.add_widget(self.to_spinner)
        root.add_widget(units_row)

        self.value_input = TextInput(
            text="10", multiline=False, font_size=dp(24),
            size_hint=(1, 0.12), padding=[dp(12), dp(14)],
        )
        self.value_input.bind(text=lambda i, v: self._recalculate())
        root.add_widget(self.value_input)

        self.result_label = Label(text="", font_size=dp(26), color=TEXT_DARK, bold=True, size_hint=(1, 0.15))
        root.add_widget(self.result_label)

        root.add_widget(Label(size_hint=(1, 1)))

        self.from_spinner.bind(text=lambda i, v: self._recalculate())
        self.to_spinner.bind(text=lambda i, v: self._recalculate())
        self._recalculate()

    def _update_bg(self, *args):
        self.bg_rect.pos = self._bg_widget.pos
        self.bg_rect.size = self._bg_widget.size

    def _back(self, instance):
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction="right")
        app.root.current = "converter_grid"

    def _recalculate(self):
        try:
            from_base = NUM_SYSTEM_BASES[self.from_spinner.text]
            to_base = NUM_SYSTEM_BASES[self.to_spinner.text]
            value = int(self.value_input.text.strip(), from_base)
            if to_base == 2:
                result = bin(value)[2:]
            elif to_base == 8:
                result = oct(value)[2:]
            elif to_base == 16:
                result = hex(value)[2:].upper()
            else:
                result = str(value)
            self.result_label.text = result
        except Exception:
            self.result_label.text = "Error"


class CalculatorApp(App):
    def build(self):
        self.title = "Calculator"
        Window.clearcolor = BG_COLOR
        self.history = []

        sm = ScreenManager(transition=SlideTransition())
        self.calc_screen = CalcScreen(name="calc")
        self.history_screen = HistoryScreen(name="history")
        self.converter_grid = ConverterGridScreen(name="converter_grid")
        self.converter_detail = ConverterDetailScreen(name="converter_detail")
        self.number_system_screen = NumberSystemScreen(name="number_system")

        sm.add_widget(self.calc_screen)
        sm.add_widget(self.history_screen)
        sm.add_widget(self.converter_grid)
        sm.add_widget(self.converter_detail)
        sm.add_widget(self.number_system_screen)
        return sm

    def add_history(self, expr, result):
        self.history.append({
            "expr": expr,
            "result": result,
            "date": datetime.now().strftime("%d/%m/%Y"),
        })


if __name__ == "__main__":
    CalculatorApp().run()