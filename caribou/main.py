import gtk.gdk as gdk
import pyatspi
import gconf
from window import CaribouWindowEntry
from keyboard import CaribouKeyboard
from i18n import _

debug = False

class Caribou:
    def __init__(self,
                 kb_factory=CaribouKeyboard,
                 window_factory=CaribouWindowEntry):
        if not self._get_a11y_enabled():
            raise Exception, "AT-SPI 1 or 2 needs to be enabled."
        self.__current_acc = None
        self.window = window_factory(kb_factory())
        pyatspi.Registry.registerEventListener(
            self.on_focus, "object:state-changed:focused")
        pyatspi.Registry.registerEventListener(self.on_focus, "focus")
        pyatspi.Registry.registerEventListener(
            self.on_text_caret_moved, "object:text-caret-moved")
        pyatspi.Registry.registerKeystrokeListener(
            self.on_key_down, mask=None, kind=(pyatspi.KEY_PRESSED_EVENT,))

    def _get_a11y_enabled(self):
        try:
            gconfc = gconf.client_get_default()
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
        self.window.set_cursor_location(gdk.Rectangle(x, y, width, height))
        
        component = acc.queryComponent()
        entry_bb = component.getExtents(pyatspi.DESKTOP_COORDS)
        self.window.set_entry_location(entry_bb)
        self.window.show_all()
       
    def __set_entry_location(self, acc):
        text = acc.queryText()
        cursor_bb = gdk.Rectangle(
            *text.getCharacterExtents(text.caretOffset,
                                      pyatspi.DESKTOP_COORDS))

        component = acc.queryComponent()
        entry_bb = component.getExtents(pyatspi.DESKTOP_COORDS)

        if cursor_bb == gdk.Rectangle(0, 0, 0, 0):
            cursor_bb = entry_bb

        self.window.set_cursor_location(cursor_bb)
        self.window.set_entry_location(entry_bb)

        self.window.show_all()
       
    def on_focus(self, event):
        acc = event.source
        if pyatspi.STATE_EDITABLE in acc.getState().getStates() or event.source_role == pyatspi.ROLE_TERMINAL:
            if event.source_role in (pyatspi.ROLE_TEXT,
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
                    self.window.hide_all()
                    self.__current_acc = None 
                    self.__set_location = None
                    if debug == True:
                        print "leave text widget in", event.host_application.name

            elif event.source_role == pyatspi.ROLE_ENTRY:
                if event.type.startswith("focus") or event.detail1 == 1:
                    self.__set_entry_location(acc)
                    self.__current_acc = event.source
                    self.__set_location = self.__set_entry_location
                    if debug == True:
                        print "enter entry widget in", event.host_application.name
                elif event.detail1 == 0:
                    self.window.hide_all()
                    self.__current_acc = None 
                    self.__set_location = None
                    if debug == True:
                        print "leave entry widget in", event.host_application.name
            else:
                print _("WARNING - Caribou: unhandled editable widget:"), event.source         

        # Firefox does report leave entry widget events.
        # This could be a way to get the entry widget leave events.
        #else:
        #    if event.detail1 == 1:
        #        self.window.hide_all()
        #        print "--> LEAVE EDITABLE TEXT <--"

    def on_key_down(self, event):
        # key binding for controlling the row column scanning
        if event.event_string == "Shift_R":
            # TODO: implement keyboard scanning
            pass 
        elif event.event_string == "Control_R":
            if debug == True:
                print "quitting ..."
            result = pyatspi.Registry.deregisterEventListener(self.on_text_caret_moved, "object:text-caret-moved")
            if debug == True:
                print "deregisterEventListener - object:text-caret-moved ...",
                if result == False:
                    print "OK"
                else:
                    print "FAIL"
            result = pyatspi.Registry.deregisterEventListener(self.on_focus, "object:state-changed:focused")
            if debug == True:
                print "deregisterEventListener - object:state-changed:focused ...",
                if result == False:
                    print "OK"
                else:
                    print "FAIL"
            result = pyatspi.Registry.deregisterEventListener(self.on_focus, "focus")
            if debug == True:
                print "deregisterEventListener - focus ...",
                if result == False:
                    print "OK"
                else:
                    print "FAIL"
            result = pyatspi.Registry.deregisterKeystrokeListener(self.on_key_down, mask=None, kind=(pyatspi.KEY_PRESSED_EVENT,))
            if debug == True:
                print "deregisterKeystrokeListener"
            gtk.main_quit()
