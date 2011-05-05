from caribou.settings.preferences_window import PreferencesDialog
from caribou.settings import CaribouSettings
from antler_settings import AntlerSettings
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Caribou
import gobject

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

        key.caribou_key.connect("notify::show-subkeys", self._on_show_subkeys)
        self._key = key

        layout = AntlerLayout()
        layout.add_row(key.caribou_key.get_extended_keys())
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

class AntlerLayout(Gtk.Grid):
    KEY_SPAN = 4

    def __init__(self, level=None):
        gobject.GObject.__init__(self)
        self.set_column_homogeneous(True)
        self.set_row_homogeneous(True)
        self.set_row_spacing(6)
        self.set_column_spacing(6)
        if level:
            self.load_rows(level.get_rows ())

    def add_row(self, row, row_num=0):
        col_num = 0
        for i, key in enumerate(row):
            antler_key = AntlerKey(key)
            self.attach(antler_key,
                        col_num + int(key.props.margin_left * self.KEY_SPAN),
                        row_num * self.KEY_SPAN,
                        int(self.KEY_SPAN * key.props.width),
                        self.KEY_SPAN)
            col_num += int((key.props.width + key.props.margin_left ) * self.KEY_SPAN)


    def load_rows(self, rows):
        for row_num, row in enumerate(rows):
            self.add_row(row.get_keys(), row_num)

class AntlerKeyboardView(Gtk.Notebook):
    def __init__(self):
        gobject.GObject.__init__(self)
        self.set_show_tabs(False)
        self.keyboard_model = Caribou.KeyboardModel()
        self.keyboard_model.connect("notify::active-group", self._on_group_changed)
        self.layers = {}
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
