from caribou.settings.preferences_window import PreferencesDialog
from caribou.settings import CaribouSettings
from antler_settings import AntlerSettings
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Caribou
import gobject
import glib
import os

PRETTY_LABELS = {
    "BackSpace" : u'\u232b',
    "space" : u' ',
    "Return" : u'\u23ce',
    'Caribou_Prefs' : u'\u2328',
    'Caribou_ShiftUp' : u'\u2b06',
    'Caribou_ShiftDown' : u'\u2b07',
    'Caribou_Emoticons' : u'\u263a',
    'Caribou_Symbols' : u'123',
    'Caribou_Symbols_More' : u'{#*',
    'Caribou_Alpha' : u'Abc'
}

class AntlerKey(Gtk.Button):
    def __init__(self, key):
        gobject.GObject.__init__(self)
        self.caribou_key = key
        self.connect("pressed", self._on_pressed)
        self.connect("released", self._on_released)
        self.set_label(self._get_key_label())

        label = self.get_child()
        label.set_use_markup(True)
        label.props.margin = 6

        ctx = self.get_style_context()
        ctx.add_class("antler-keyboard-button")

        if key.props.name == "Caribou_Prefs":
            key.connect("key-clicked", self._on_prefs_clicked)
        if key.get_extended_keys ():
            self._sublevel = AntlerSubLevel(self)

    def _on_prefs_clicked(self, key):
        p = PreferencesDialog(AntlerSettings())
        p.populate_settings(CaribouSettings())
        p.show_all()
        p.run()
        p.destroy()

    def _get_key_label(self):
        label = self.caribou_key.props.name
        if PRETTY_LABELS.has_key(self.caribou_key.props.name):
            label = PRETTY_LABELS[self.caribou_key.props.name]
        elif self.caribou_key.props.name.startswith('Caribou_'):
            label = self.caribou_key.name.replace('Caribou_', '')
        else:
            unichar = unichr(Gdk.keyval_to_unicode(self.caribou_key.props.keyval))
            if not unichar.isspace() and unichar != u'\x00':
                label = unichar

        return "<b>%s</b>" % glib.markup_escape_text(label.encode('utf-8'))

    def _on_pressed(self, button):
        self.caribou_key.press()

    def _on_released(self, button):
        self.caribou_key.release()

    def do_get_preferred_width_for_height(self, w):
        return (w, w)

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.WIDTH_FOR_HEIGHT

class AntlerSubLevel(Gtk.Window):
    def __init__(self, key):
        gobject.GObject.__init__(self, type=Gtk.WindowType.POPUP)

        self.set_decorated(False)
        self.set_resizable(False)
        self.set_accept_focus(False)
        self.set_position(Gtk.WindowPosition.MOUSE)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)

        ctx = self.get_style_context()
        ctx.add_class("antler-keyboard-window")

        key.caribou_key.connect("notify::show-subkeys", self._on_show_subkeys)
        self._key = key

        layout = AntlerLayout()
        layout.add_row([key.caribou_key.get_extended_keys()])
        self.add(layout)

    def _on_show_subkeys(self, key, prop):
        parent = self._key.get_toplevel()
        if key.props.show_subkeys:
            self.set_transient_for(parent)
            parent.set_sensitive(False)
            self.show_all()
        else:
            parent.set_sensitive(True)
            self.hide()

class AntlerLayout(Gtk.HBox):
    KEY_SPAN = 4

    def __init__(self, level=None):
        gobject.GObject.__init__(self)
        self.set_spacing(12)
        self._columns = []
        self._keys_map = {}
        self._active_scan_group = []
        self._dwelling_scan_group = []

        ctx = self.get_style_context()
        ctx.add_class("antler-keyboard-layout")

        if level:
            self.load_rows(level.get_rows ())

    def add_column (self):
        col = Gtk.Grid()
        col.set_column_homogeneous(True)
        col.set_row_homogeneous(True)
        col.set_row_spacing(6)
        col.set_column_spacing(6)
        self.add (col)
        self._columns.append(col)
        return col


    def add_row(self, row, row_num=0):
        x = 0
        for c, col in enumerate(row):
            try:
                column = self._columns[c]
            except IndexError:
                column = self.add_column()

            for i, key in enumerate(col):
                antler_key = AntlerKey(key)
                self._keys_map[key] = antler_key
                ctx = antler_key.get_style_context()
                ctx.add_class("antler-keyboard-row%d" % row_num)
                column.attach(antler_key,
                              x + int(key.props.margin_left * self.KEY_SPAN),
                              row_num * self.KEY_SPAN,
                              int(self.KEY_SPAN * key.props.width),
                              self.KEY_SPAN)
                x += int((key.props.width + key.props.margin_left ) * self.KEY_SPAN)

    def load_rows(self, rows):
        for row_num, row in enumerate(rows):
            self.add_row([c.get_keys() for c in row.get_columns()], row_num)

class AntlerKeyboardView(Gtk.Notebook):
    def __init__(self):
        gobject.GObject.__init__(self)
        self.set_show_tabs(False)
        self.keyboard_model = Caribou.KeyboardModel()
        self.keyboard_model.connect("notify::active-group", self._on_group_changed)

        self.layers = {}


        settings = AntlerSettings()
        use_system = settings.use_system
        use_system.connect("value-changed", self._on_use_system_theme_changed)

        self._app_css_provider = Gtk.CssProvider()
        self._load_style(
            self._app_css_provider, "style.css",
            [glib.get_user_data_dir()] + list(glib.get_system_data_dirs()))

        if not use_system.value:
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(), self._app_css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


        self._scan_css_provider = Gtk.CssProvider()
        self._load_style(
            self._scan_css_provider, "scan-style.css",
            [glib.get_user_data_dir()] + list(glib.get_system_data_dirs()))
        Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(), self._scan_css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self._user_css_provider = Gtk.CssProvider()
        self._load_style(self._user_css_provider, "user-style.css",
                         [glib.get_user_data_dir()])
        Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(), self._user_css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)

        for gname in self.keyboard_model.get_groups():
            group = self.keyboard_model.get_group(gname)
            self.layers[gname] = {}
            group.connect("notify::active-level", self._on_level_changed)
            for lname in group.get_levels():
                level = group.get_level(lname)
                layout = AntlerLayout(level)
                layout.show()
                self.layers[gname][lname] = self.append_page(layout, None)

        self._set_to_active_layer()

    def _on_use_system_theme_changed(self, setting, value):
        if value:
            Gtk.StyleContext.remove_provider_for_screen(
                Gdk.Screen.get_default(), self._app_css_provider)
        else:
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(), self._app_css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _load_style(self, provider, filename, search_path):
        spath = search_path[:]
        if os.environ.has_key("ANTLER_THEME_PATH"):
            spath.insert(0, os.environ["ANTLER_THEME_PATH"])

        for directory in spath:
            fn = os.path.join(directory, "antler", filename)
            if os.path.exists(fn):
                provider.load_from_path(fn)
                break

    def _on_level_changed(self, group, prop):
        self._set_to_active_layer()

    def _on_group_changed(self, kb, prop):
        self._set_to_active_layer()

    def _set_to_active_layer(self):
        active_group_name = self.keyboard_model.props.active_group
        active_group = self.keyboard_model.get_group(active_group_name)
        active_level_name = active_group.props.active_level

        self.set_current_page(self.layers[active_group_name][active_level_name])

if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    w = Gtk.Window()
    w.set_accept_focus(False)

    kb = AntlerKeyboardView()
    w.add(kb)

    w.show_all()

    Gtk.main()
