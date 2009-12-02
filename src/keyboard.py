# -*- coding: utf-8 -*-
#
# Carbou - text entry and UI navigation application
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
from keyboards import qwerty
import rsvg
import cairo

class CaribouPredicitionArea(gtk.HBox):
    pass

# TODO validate keyboard by creating this object and catching exception
class CaribouKeyboard(gtk.Frame):

    def __init__(self, keyboard):
        gtk.Frame.__init__(self)
        self.set_shadow_type(gtk.SHADOW_NONE)

        self._vk = virtkey.virtkey()

        layouts, switch_buttons = [], []
        for layout in keyboard.layouts:
            layoutvbox = gtk.VBox(homogeneous=True)
            layoutvbox.set_name(layout)
            layout = getattr(keyboard, layout)
            for row in layout:
                rowhbox = gtk.HBox(homogeneous=True)
                for key in row:
                    # check if the key is a simple str or a key defined by a tuple
                    if isinstance(key, str):
                        if key == "cf":
                            # configuration key
                            button = gtk.Button()
                            image = gtk.image_new_from_pixbuf(
                                button.render_icon(gtk.STOCK_PREFERENCES,
                                                   gtk.ICON_SIZE_BUTTON))
                            button.set_image(image)
                            button.set_name ("configuration")
                            switch_buttons.append(button)
                        else:
                            # single utf-8 character key
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

                layoutvbox.pack_start(rowhbox, expand=False, fill=True)

            layouts.append(layoutvbox)

        # add configuration window to layouts
        # TODO use gtkBuilder
        confhbox = gtk.HBox(homogeneous=True)
        # return to first keyboard layout from configuration window
        button = gtk.Button("abc") # FIXME use keyboard image
        button.set_name(layouts[0].get_name())
        switch_buttons.append(button)
        confhbox.pack_start(button)

        confhbox.pack_start(gtk.Label("configuration coming soon"))
        confhbox.set_name("configuration")
        layouts.append(confhbox)

        # connect the change layout buttons
        for button in switch_buttons:
            for layout in layouts:
                if button.get_name() == layout.get_name():
                    button.connect("clicked", self.__change_layout, layout)
                    button.set_name("")
                    break
            else:
                print "ERROR" # TODO throw exception

        # add the first layout and make it visible
        self.add(layouts[0])
        del layouts
        del switch_buttons
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

class CaribouWindow(gtk.VBox):
    __gtype_name__ = "CaribouWindow"

    def __init__(self):
        super(CaribouWindow, self).__init__()
        self.set_name("CaribouWindow")

        self.__toplevel = gtk.Window(gtk.WINDOW_POPUP)
        self.__toplevel.add(self)
        self.__toplevel.connect("size-allocate", lambda w, a: self.__check_position())
        self.__cursor_location = (0, 0)
        self.pack_start(CaribouKeyboard(qwerty))

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

