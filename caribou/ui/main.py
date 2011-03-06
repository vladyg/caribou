import pyatspi
from gi.repository import GConf
from gi.repository import Gtk
from gi.repository import Gdk

from window import CaribouWindowEntry, Rectangle
from keyboard import CaribouKeyboard
from caribou.common.settings_manager import SettingsManager
from caribou.ui.i18n import _
import caribou.common.const as const
from scan import ScanMaster

debug = False

class Caribou:
    def __init__(self,
                 kb_factory=CaribouKeyboard,
                 window_factory=CaribouWindowEntry):
        if not self._get_a11y_enabled():
            raise Exception, "AT-SPI 1 or 2 needs to be enabled."
        self.__current_acc = None
        self.window_factory = window_factory
        self.kb_factory = kb_factory
        kb = kb_factory()
        self.window = window_factory(kb)
        self.client = GConf.Client.get_default()
        self._register_event_listeners()
        SettingsManager.layout.connect("value-changed",
                                       self._on_layout_changed)

        # Scanning
        self.scan_master = ScanMaster(self.window, kb)
        SettingsManager.scan_enabled.connect("value-changed",
                                             self._on_scan_toggled)
        if SettingsManager.scan_enabled.value:
            self.scan_master.start()

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
            gconfc = GConf.Client.get_default()
            atspi1 = gconfc.get_bool("/desktop/gnome/interface/accessibility")
            atspi2 = gconfc.get_bool("/desktop/gnome/interface/accessibility2")
            return atspi1 or atspi2
        except:
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
        
        
