import pyatspi
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from string import Template

from window import CaribouWindowEntry, Rectangle
from keyboard import CaribouKeyboard
from caribou.common.settings_manager import SettingsManager
from caribou.ui.i18n import _
import caribou.common.const as const
from scan import ScanMaster

debug = False

CSS_TEMPLATE = """
.caribou-keyboard-button {
background-image: none;
background-color: $normal_bg;
}

.caribou-keyboard-button:hover {
background-image: none;
background-color: $mouseover_bg;
}
"""

SCAN_CSS_TEMPLATE = """
.caribou-scan-key {
background-image: none;
background-color: $button_scan;
}

.caribou-scan-row {
background-image: none;
background-color: $row_scan;
}

.caribou-scan-block {
background-image: none;
background-color: $block_scan;
}

.caribou-scan-cancel {
background-image: none;
background-color: $cancel_scan;
}
"""

class Caribou:
    def __init__(self,
                 kb_factory=CaribouKeyboard,
                 window_factory=CaribouWindowEntry):
        if not self._get_a11y_enabled():
            msgdialog = Gtk.MessageDialog(None,
                                          Gtk.DialogFlags.MODAL,
                                          Gtk.MessageType.QUESTION,
                                          Gtk.ButtonsType.YES_NO,
                                          _("In order to use %s, accessibility needs "
                                            "to be enabled. Do you want to enable "
                                            "it now?") % const.APP_NAME)
            resp = msgdialog.run()
            if resp == Gtk.ResponseType.NO:
                msgdialog.destroy()
                quit()
            if resp == Gtk.ResponseType.YES:
                settings = Gio.Settings('org.gnome.desktop.interface')
                atspi = settings.set_boolean("toolkit-accessibility", True)
                msgdialog2 = Gtk.MessageDialog(msgdialog,
                                               Gtk.DialogFlags.MODAL,
                                               Gtk.MessageType.INFO,
                                               Gtk.ButtonsType.OK,
                                               _("Accessibility has been enabled. "
                                                 "Log out and back in again to use "
                                                 "%s." % const.APP_NAME))
                msgdialog2.run()
                msgdialog2.destroy()
                msgdialog.destroy()
                quit()
        self.__current_acc = None
        self.window_factory = window_factory
        self.kb_factory = kb_factory
        kb = kb_factory()
        self.window = window_factory(kb)
        self._register_event_listeners()
        SettingsManager.layout.connect("value-changed",
                                       self._on_layout_changed)

        # Scanning
        self.scan_master = ScanMaster(self.window, kb)
        SettingsManager.scan_enabled.connect("value-changed",
                                             self._on_scan_toggled)
        if SettingsManager.scan_enabled.value:
            self.scan_master.start()

        self._custom_css_provider = Gtk.CssProvider()

        for name in ["normal_color", "mouse_over_color", "default_colors"]:
            getattr(SettingsManager, name).connect("value-changed",
                                                   self._colors_changed)
        self._colors_changed(None, None)

        self._scan_css_provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self._scan_css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        for name in ["button_scanning_color",
                     "row_scanning_color",
                     "block_scanning_color",
                     "cancel_scanning_color"]:
            getattr(SettingsManager, name).connect("value-changed",
                                                   self._scan_colors_changed)
        self._scan_colors_changed(None, None)

    def _colors_changed(self, setting, value):
        if SettingsManager.default_colors.value:
            Gtk.StyleContext.remove_provider_for_screen(
                Gdk.Screen.get_default(),
                self._custom_css_provider)
        else:
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                self._custom_css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            self._custom_css_provider.load_from_data(
                Template(CSS_TEMPLATE).substitute(
                    normal_bg=SettingsManager.normal_color.value,
                    mouseover_bg=SettingsManager.mouse_over_color.value), -1)

    def _scan_colors_changed(self, setting, value):
        self._scan_css_provider.load_from_data(Template(SCAN_CSS_TEMPLATE).substitute(
                button_scan=SettingsManager.button_scanning_color.value,
                row_scan=SettingsManager.row_scanning_color.value,
                block_scan=SettingsManager.block_scanning_color.value,
                cancel_scan=SettingsManager.cancel_scanning_color.value), -1)


    def _register_event_listeners(self):
        pyatspi.Registry.registerEventListener(
            self.on_focus, "object:state-changed:focused")
        pyatspi.Registry.registerEventListener(self.on_focus, "focus")
        pyatspi.Registry.registerEventListener(
            self.on_text_caret_moved, "object:text-caret-moved")

    def _deregister_event_listeners(self):
        pyatspi.Registry.deregisterEventListener(
            self.on_focus, "object:state-changed:focused")
        pyatspi.Registry.deregisterEventListener(self.on_focus, "focus")
        pyatspi.Registry.deregisterEventListener(
            self.on_text_caret_moved, "object:text-caret-moved")

    def _on_scan_toggled(self, setting, val):
        if val:
            self.scan_master.start()
        else:
            self.scan_master.stop()

    def _on_layout_changed(self, setting, val):
        self._deregister_event_listeners()
        self.window.destroy()
        self._update_window()
        self._register_event_listeners()

    def _update_window(self):
        kb = self.kb_factory()
        self.scan_master.set_keyboard(kb)
        self.window = self.window_factory(kb)

    def _get_a11y_enabled(self):
        try:
            try:
                settings = Gio.Settings('org.gnome.desktop.interface')
                atspi = settings.get_boolean("toolkit-accessibility")
                print "->", atspi
                return atspi
            except:
                raise
                from gi.repository import GConf
                gconfc = GConf.Client.get_default()
                atspi1 = gconfc.get_bool(
                    "/desktop/gnome/interface/accessibility")
                atspi2 = gconfc.get_bool(
                    "/desktop/gnome/interface/accessibility2")
                return atspi1 or atspi2
        except:
            raise
            return False

    def on_text_caret_moved(self, event):
        if self.__current_acc == event.source:
            self.__set_location(event.source)
            if debug == True:
                print "object:text-caret-moved in", event.host_application.name,
                print event.detail1, event.source.description

    def __set_text_location(self, acc):
        text = acc.queryText()
        [x, y, width, height] = text.getCharacterExtents(text.caretOffset, pyatspi.DESKTOP_COORDS)
        self.window.set_cursor_location(Rectangle(x, y, width, height))

        component = acc.queryComponent()
        entry_bb = component.getExtents(pyatspi.DESKTOP_COORDS)
        self.window.set_entry_location(entry_bb)
        self.window.show_all()

    def __set_entry_location(self, acc):
        text = acc.queryText()
        cursor_bb = Rectangle(
            *text.getCharacterExtents(text.caretOffset,
                                      pyatspi.DESKTOP_COORDS))

        component = acc.queryComponent()
        entry_bb = component.getExtents(pyatspi.DESKTOP_COORDS)

        if cursor_bb == Rectangle(0, 0, 0, 0):
            cursor_bb = entry_bb

        self.window.set_cursor_location(cursor_bb)
        self.window.set_entry_location(entry_bb)

        self.window.show_all()

    def on_focus(self, event):
        acc = event.source
        source_role = acc.getRole()
        if acc.getState().contains(pyatspi.STATE_EDITABLE) or \
                source_role == pyatspi.ROLE_TERMINAL:
            if source_role in (pyatspi.ROLE_TEXT,
                               pyatspi.ROLE_PARAGRAPH,
                               pyatspi.ROLE_PASSWORD_TEXT,
                               pyatspi.ROLE_TERMINAL):
                if event.type.startswith("focus") or event.detail1 == 1:
                    self.__set_text_location(acc)
                    self.__current_acc = event.source
                    self.__set_location = self.__set_text_location
                    if debug == True:
                        print "enter text widget in", event.host_application.name
                elif event.detail1 == 0 and acc == self.__current_acc:
                    self.window.hide()
                    self.__current_acc = None
                    self.__set_location = None
                    if debug == True:
                        print "leave text widget in", event.host_application.name

            elif source_role == pyatspi.ROLE_ENTRY:
                if event.type.startswith("focus") or event.detail1 == 1:
                    self.__set_entry_location(acc)
                    self.__current_acc = event.source
                    self.__set_location = self.__set_entry_location
                    if debug == True:
                        print "enter entry widget in", event.host_application.name
                elif event.detail1 == 0:
                    self.window.hide()
                    self.__current_acc = None
                    self.__set_location = None
                    if debug == True:
                        print "leave entry widget in", event.host_application.name
            else:
                if debug == True:
                    print _("WARNING - Caribou: unhandled editable widget:"), event.source

        # Firefox does not report leave entry widget events.
        # This could be a way to get the entry widget leave events.
        #else:
        #    if event.detail1 == 1:
        #        self.window.hide()
        #        print "--> LEAVE EDITABLE TEXT <--"

    def clean_exit(self):
        self.scan_master.stop()
        self._deregister_event_listeners()


