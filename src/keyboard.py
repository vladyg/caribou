# -*- coding: UTF-8 -*-

import gtk
import gobject
import gtk.gdk as gdk
import pango
import virtkey
import qwerty

class CaribouPredicitionArea(gtk.HBox):
    pass

class CaribouKeyboard(gtk.Frame):

    def __init__(self):
        gtk.Frame.__init__(self)
        self.set_shadow_type(gtk.SHADOW_NONE)

        self._layouts = []
        self._vk = virtkey.virtkey()

        for layout in qwerty.keyboard:
            layoutvbox = gtk.VBox(homogeneous=True)
            for row in layout:
                rowhbox = gtk.HBox(homogeneous=True)
                for key in row:
                    # check if the key is a simple str or a key defined by a tuple
                    if isinstance(key, str):
                        button = gtk.Button(key)
                        char = ord(key.decode('utf-8'))
                        button.connect("clicked", lambda w, d: self.__send_unicode(d), char)
                    elif isinstance(key, tuple):
                        button = gtk.Button(key[0])
                        # check if this key is a layout switch key or not
                        if isinstance(key[1], str):
                            # switch layout key
                            button.connect("clicked", lambda w, d: self.__switch_layout(d), key[0])
                        else:
                            # regular key
                            button.connect("clicked", lambda w, d: self.__send_keysym(d), key[1])
                    else:
                        pass #TODO throw error here

                    rowhbox.pack_start(button, expand=False, fill=True)

                layoutvbox.pack_start(rowhbox, expand=False, fill=False)
            self._layouts.append(layoutvbox)

        # add the first layer and make it visible
        self.add(self._layouts[0])
        self.show_all()

    def __send_unicode(self, char):
        self._vk.press_unicode(char)
        self._vk.release_unicode(char)

    def __send_keysym(self, keysym):
        self._vk.press_keysym(keysym)
        self._vk.release_keysym(keysym)

    def __switch_layout(self, data):
        if data == "⇧":
            self.remove(self._layouts[0])
            self.add(self._layouts[1])
            self.show_all()
        elif data == "⇩":
            self.remove(self._layouts[1])
            self.add(self._layouts[0])
            self.show_all()

gobject.type_register(CaribouKeyboard)

class CaribouWindow(gtk.VBox):
    __gtype_name__ = "CaribouWindow"

    def __init__(self):
        super(CaribouWindow, self).__init__()
        self.set_name("CaribouWindow")

        self.__toplevel = gtk.Window(gtk.WINDOW_POPUP)
        self.__toplevel.add(self)
        self.__toplevel.connect("size-allocate", lambda w, a: self.__check_position())
        self.__cursor_location = (0, 0)
        self.pack_start(CaribouKeyboard())

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
    ckbd = CaribouWindow()
    ckbd.show_all()
    gtk.main()

