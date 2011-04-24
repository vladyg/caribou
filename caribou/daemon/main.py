import pyatspi
import dbus
from gi.repository import Gio
from string import Template

from caribou.i18n import _
from caribou import APP_NAME

debug = False

class CaribouDaemon:
    def __init__(self, keyboard_name="Antler"):
        if not self._get_a11y_enabled():
            self._show_no_a11y_dialogs()
        bus = dbus.SessionBus()
        try:
            dbus_obj = bus.get_object("org.gnome.Caribou.%s" % keyboard_name,
                                      "/org/gnome/Caribou/%s" % keyboard_name)
        except dbus.DBusException:
            print "%s is not running, and is not provided by any .service file" % \
                keyboard_name
            return
        self.keyboard_proxy = dbus.Interface(dbus_obj, "org.gnome.Caribou.Keyboard")
        self._current_acc = None
        self._register_event_listeners()

    def _show_no_a11y_dialogs(self):
        from gi.repository import Gtk
        msgdialog = Gtk.MessageDialog(None,
                                      Gtk.DialogFlags.MODAL,
                                      Gtk.MessageType.QUESTION,
                                      Gtk.ButtonsType.YES_NO,
                                      _("In order to use %s, accessibility needs "
                                        "to be enabled. Do you want to enable "
                                        "it now?") % APP_NAME)
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
                                             "%s." % APP_NAME))
            msgdialog2.run()
            msgdialog2.destroy()
            msgdialog.destroy()
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

    def _get_a11y_enabled(self):
        try:
            try:
                settings = Gio.Settings('org.gnome.desktop.interface')
                atspi = settings.get_boolean("toolkit-accessibility")
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
        if self._current_acc == event.source:
            text = self._current_acc.queryText()
            x, y, w, h = text.getCharacterExtents(text.caretOffset,
                                                  pyatspi.DESKTOP_COORDS)
            if (x, y, w, h) == (0, 0, 0, 0):
                component = self._current_acc.queryComponent()
                bb = component.getExtents(pyatspi.DESKTOP_COORDS)
                x, y, w, h = bb.x, bb.y, bb.width, bb.height

            self.keyboard_proxy.SetCursorLocation(x, y, w, h)
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

        self.keyboard_proxy.SetCursorLocation(bx, by, bw, bh)

        self.keyboard_proxy.SetEntryLocation(entry_bb.x, entry_bb.y,
                                             entry_bb.width, entry_bb.height)

        self.keyboard_proxy.Show()

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
                    self.keyboard_proxy.Hide()
                    self._current_acc = None
                    if debug == True:
                        print "leave text widget in", event.host_application.name
            else:
                if debug == True:
                    print _("WARNING - Caribou: unhandled editable widget:"), \
                        event.source

    def clean_exit(self):
        self._deregister_event_listeners()


