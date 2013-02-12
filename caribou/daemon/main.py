import pyatspi
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import GdkX11

from string import Template

from caribou.i18n import _
from caribou import APP_NAME

debug = False

class CaribouDaemon:
    def __init__(self):
        try:
            self.keyboard_proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION,
                Gio.DBusProxyFlags.NONE,
                None,
                "org.gnome.Caribou.Keyboard",
                "/org/gnome/Caribou/Keyboard",
                "org.gnome.Caribou.Keyboard",
                None)
        except GLib.GError, e:
            self._show_error_dialog(e.message)
        self._current_acc = None
        self._x11_display = GdkX11.X11Display.get_default()
        self._register_event_listeners()

    def _show_error_dialog(self, message):
        from gi.repository import Gtk
        msgdialog = Gtk.MessageDialog(None,
                                      Gtk.DialogFlags.MODAL,
                                      Gtk.MessageType.ERROR,
                                      Gtk.ButtonsType.CLOSE,
                                      _("Error starting %s") % APP_NAME)
        msgdialog.format_secondary_text(message)
        msgdialog.run()
        quit()

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

    def on_text_caret_moved(self, event):
        if self._current_acc == event.source:
            text = self._current_acc.queryText()
            x, y, w, h = text.getCharacterExtents(text.caretOffset,
                                                  pyatspi.DESKTOP_COORDS)
            if (x, y, w, h) == (0, 0, 0, 0):
                component = self._current_acc.queryComponent()
                bb = component.getExtents(pyatspi.DESKTOP_COORDS)
                x, y, w, h = bb.x, bb.y, bb.width, bb.height

            self.keyboard_proxy.SetCursorLocation('(iiii)', x, y, w, h)
            if debug == True:
                print "object:text-caret-moved in", event.host_application.name,
                print event.detail1, event.source.description

    def _set_entry_location(self, acc):
        text = acc.queryText()
        bx, by, bw, bh = text.getCharacterExtents(text.caretOffset,
                                                  pyatspi.DESKTOP_COORDS)

        component = acc.queryComponent()
        entry_bb = component.getExtents(pyatspi.DESKTOP_COORDS)

        if (bx, by, bw, bh) == (0, 0, 0, 0):
            bx, by, bw, bh = entry_bb.x, entry_bb.y, entry_bb.width, entry_bb.height

        self.keyboard_proxy.SetCursorLocation('(iiii)', bx, by, bw, bh)

        self.keyboard_proxy.SetEntryLocation('(iiii)', entry_bb.x, entry_bb.y,
                                             entry_bb.width, entry_bb.height)

        self.keyboard_proxy.Show('(u)', self._x11_display.get_user_time())

    def on_focus(self, event):
        acc = event.source
        source_role = acc.getRole()
        if acc.getState().contains(pyatspi.STATE_EDITABLE) or \
                source_role == pyatspi.ROLE_TERMINAL:
            if source_role in (pyatspi.ROLE_TEXT,
                               pyatspi.ROLE_PARAGRAPH,
                               pyatspi.ROLE_PASSWORD_TEXT,
                               pyatspi.ROLE_TERMINAL,
                               pyatspi.ROLE_ENTRY):
                if event.type.startswith("focus") or event.detail1 == 1:
                    self._set_entry_location(acc)
                    self._current_acc = event.source
                    if debug == True:
                        print "enter text widget in", event.host_application.name
                elif event.detail1 == 0 and acc == self._current_acc:
                    self.keyboard_proxy.Hide('(u)',
                                             self._x11_display.get_user_time())
                    self._current_acc = None
                    if debug == True:
                        print "leave text widget in", event.host_application.name
            else:
                if debug == True:
                    print _("WARNING - Caribou: unhandled editable widget:"), \
                        event.source

    def clean_exit(self):
        self.keyboard_proxy.Hide('(u)', self._x11_display.get_user_time())
        self._deregister_event_listeners()

    def run(self):
        try:
            pyatspi.Registry.start()
        except KeyboardInterrupt:
            self.clean_exit()
            pyatspi.Registry.stop()
