# -*- coding: utf-8 -*-
#
# Carbou - On-screen Keyboard and UI navigation application
#
# Copyright (C) 2009 Adaptive Technology Resource Centre
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import gtk
import gobject
import gtk.gdk as gdk
import pango
import virtkey
import qwerty

class CaribouPredicitionArea(gtk.HBox):
    pass

# TODO validate keyboard by creating this object and catching exception
class CaribouKeyboard(gtk.Frame):

    def __init__(self, keyboard):
        gtk.Frame.__init__(self)
        self.set_shadow_type(gtk.SHADOW_NONE)

        # FIXME use references instead of this??
        self._layouts = []
        self._vk = virtkey.virtkey()

        switch_buttons = []
        for layout in keyboard.layouts:
            layoutvbox = gtk.VBox(homogeneous=True)
            layoutvbox.set_name(layout)
            layout = getattr(keyboard, layout)
            for row in layout:
                rowhbox = gtk.HBox(homogeneous=True)
                for key in row:
                    # check if the key is a simple str or a key defined by a tuple
                    if isinstance(key, str):
                        button = gtk.Button(key)
                        char = ord(key.decode('utf-8'))
                        button.connect("clicked", self.__send_unicode, char)
                    elif isinstance(key, tuple):
                        button = gtk.Button(key[0])
                        # check if this key is a layout switch key or not
                        if isinstance(key[1], str):
                            # switch layout key
                            # set layer name on button and save to process later
                            button.set_name(key[1])
                            switch_buttons.append(button)
                        else:
                            # regular key
                            button.connect("clicked", self.__send_keysym, key[1])
                    else:
                        pass #TODO throw error here

                    rowhbox.pack_start(button, expand=False, fill=True)

                layoutvbox.pack_start(rowhbox, expand=False, fill=False)

            self._layouts.append(layoutvbox)

        for button in switch_buttons:
            for layout in self._layouts:
                if button.get_name() == layout.get_name():
                    button.connect("clicked", self.__change_layout, layout)
                    button.set_name("")
                    break
            else:
                print "ERROR" # TODO throw exception

        # add the first layer and make it visible
        self.add(self._layouts[0])
        self.show_all()

    def __send_unicode(self, widget, data):
        self._vk.press_unicode(data)
        self._vk.release_unicode(data)

    def __send_keysym(self, widget, data):
        self._vk.press_keysym(data)
        self._vk.release_keysym(data)

    def __change_layout(self, widget, data):
        self.remove(self.get_child())
        self.add(data)
        self.show_all()

gobject.type_register(CaribouKeyboard)

class CaribouWindow(gtk.Window):
    __gtype_name__ = "CaribouWindow"

    def __init__(self):
        super(CaribouWindow, self).__init__(gtk.WINDOW_POPUP)
        self.set_name("CaribouWindow")

        self._vbox = gtk.VBox()
        self.add(self._vbox)

        self.connect("size-allocate", lambda w, a: self._update_position())

        self._vbox.pack_start(CaribouKeyboard(qwerty))

class CaribouHoverWindow(CaribouWindow):
    __gtype_name__ = "CaribouHoverWindow"
    def __init__(self):
        super(CaribouHoverWindow, self).__init__()
        self._cursor_location = gtk.gdk.Rectangle()

    def _set_cursor_location(self, val):
        self._cursor_location = val
        self._update_position()

    def _get_cursor_location(self):
        return self._cursor_location

    cursor_location = gobject.property(type=object, 
                                       setter=_set_cursor_location,
                                       getter=_get_cursor_location)

    def _update_position(self):
        #print "---->>> CHECK POSITION"
        bx = self.cursor_location.x + self.allocation.width
        by = self.cursor_location.y + self.allocation.height

        root_window = gdk.get_default_root_window()
        sx, sy = root_window.get_size()

        if bx > sx:
            x = sx - self.allocation.width
        else:
            x = self.cursor_location.x

        if by > sy:
            y = self.cursor_location.y - self.allocation.height
        else:
            y = self.cursor_location.y + self.cursor_location.height

        self.move(x, y)

class CaribouKeyboardPlacement:
    LEFT = 0
    RIGHT = 1
    TOP = 0
    BOTTOM = 1
    CENTER = 2

    SCREEN = 0
    ENTRY = 1
    CURSOR = 2

    INSIDE = 0
    OUTSIDE = 1

    

if __name__ == "__main__":
    ckbd = CaribouHoverWindow()
    ckbd.show_all()
    gtk.main()

