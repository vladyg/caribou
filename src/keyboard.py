# -*- coding: UTF-8 -*-

import candidatepanel
import gtk
import gobject
import gtk.gdk as gdk
import pango
import virtkey


# from OnBoard.utils.py
keysyms = {"space"     : 0xff80,
           "insert"    : 0xff9e,
           "home"      : 0xff50,
           "page_up"   : 0xff55,
           "page_down" : 0xff56,
           "end"       : 0xff57,
           "delete"    : 0xff9f,
           "return"    : 0xff0d,
           "backspace" : 0xff08,
           "left"      : 0xff51,
           "up"        : 0xff52,
           "right"     : 0xff53,
           "down"      : 0xff54,}

# TODO add horizonal keysize - will be able to specify a mulitplier
# TODO add key colour

backspace = ("⌫", keysyms["backspace"])
control = (".?12", keysyms["space"]) #TODO not implemented

# key format ("label", keysym, size) 
layout = ( ("q", "w", "e", "r", "t", "y", "u", "i", "o", "p"),
           ("a", "s", "d", "f", "g", "h", "j", "k", "l", backspace ),
           ("z", "x", "c", "v", "b", "n", "m", " ", control, "⇧") )

# TODO add keyboard layers 
#layout2 = ( ("Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"),
#            ("A", "S", "D", "F", "G", "H", "J", "K", "L", backspace ),
#            ("Z", "X", "C", "V", "B", "N", "M", " ", " ", "⇧") )

class CaribouPredicitionArea(gtk.HBox):
    pass

class CaribouKey(gtk.Button):
    __gtype_name__ = "CaribouKey"

    def __init__(self, key, vk):
       if isinstance(key, tuple):
           label = key[0]
           keysym = key[1]
           self.__press_key = vk.press_keysym
           self.__release_key = vk.release_keysym
       elif isinstance(key, str):
           label = key
           keysym = ord(key.decode('utf-8'))
           self.__press_key = vk.press_unicode
           self.__release_key = vk.release_unicode
       else:
           pass #TODO throw error here 
       gtk.Button.__init__(self, label)
       #self.set_relief(gtk.RELIEF_NONE)
       self.connect("clicked", self.__on_click, keysym)

    def __on_click(self, widget, data):
        self.__press_key(data)
        self.__release_key(data)
       
gobject.type_register(CaribouKey)

class CaribouKeyboard(gtk.VBox):
    __gtype_name__ = "CaribouKeyboard"

    def __init__(self):
        super(CaribouKeyboard, self).__init__()
        self.set_name("CaribouKeyboard")

        self.__toplevel = gtk.Window(gtk.WINDOW_POPUP)
        self.__toplevel.add(self)
        self.__toplevel.connect("size-allocate", lambda w, a: self.__check_position())

        self.__cursor_location = (0, 0)

        self.__build_keyboard()


    #TODO: validate keyboard
    def __build_keyboard(self):
        vk = virtkey.virtkey()
        for row in layout:
            rowhbox = gtk.HBox(homogeneous=True)
            for keylabel in row:
                key = CaribouKey(keylabel, vk)
                rowhbox.pack_start(key, expand=False, fill=True)
            self.pack_start(rowhbox, expand=False, fill=False)
        
    #TODO understand
    def set_cursor_location(self, x, y):
        #print "----> SET CURSOR LOCATION"
        self.__cursor_location = (x, y)
        self.__check_position()

    def do_size_request(self, requisition):
        #print "---->> DO SIZE REQUEST"
        gtk.VBox.do_size_request(self, requisition)
        self.__toplevel.resize(1, 1)

    def __check_position(self):
        #print "---->>> CHECK POSITION"
        bx = self.__cursor_location[0] + self.__toplevel.allocation.width
        by = self.__cursor_location[1] + self.__toplevel.allocation.height

        root_window = gdk.get_default_root_window()
        sx, sy = root_window.get_size()

        if bx > sx:
            x = sx - self.__toplevel.allocation.width
        else:
            x = self.__cursor_location[0]

        if by > sy:
            y = sy - self.__toplevel.allocation.height
        else:
            y = self.__cursor_location[1]

        self.move(x, y)

    def show_all(self):
        gtk.VBox.show_all(self)
        self.__toplevel.show_all()

    def hide_all(self):
        gtk.VBox.hide_all(self)
        self.__toplevel.hide_all()

    def move(self, x, y):
        self.__toplevel.move(x, y)

if __name__ == "__main__":
    ckbd = CaribouKeyboard()
    ckbd.show_all()
    gtk.main()

