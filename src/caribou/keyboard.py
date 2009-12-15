# -*- coding: utf-8 -*-
#
# Caribou - text entry and UI navigation application
#
# Copyright (C) 2009 Adaptive Technology Resource Centre
#  * Contributor: Ben Konrath <ben@bagu.org>
# Copyright (C) 2009 Eitan Isaacson <eitan@monotonous.org>
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
import virtkey
from keyboards import qwerty

class CaribouPredicitionArea(gtk.HBox):
    pass

# TODO validate keyboard by creating this object and catching exception
class CaribouKeyboard(gtk.Frame):
    __gtype_name__ = "CaribouKeyboard"

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

        # add preferences layout
        image = gtk.Image()
        image.set_from_icon_name("gnome-dev-keyboard", gtk.ICON_SIZE_BUTTON)
        button = gtk.Button()
        button.set_image(image)
        button.set_name(layouts[0].get_name())
        switch_buttons.append(button)

        confhbox = gtk.HBox()
        confhbox.pack_start(button)
        confhbox.pack_start(gtk.Label("configuration coming soon"))

        confvbox = gtk.VBox(homogeneous=True)
        confvbox.pack_start(confhbox)
        confvbox.pack_start(gtk.HBox())
        confvbox.pack_start(gtk.HBox())
        confvbox.set_name("configuration")
        layouts.append(confvbox)

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


if __name__ == "__main__":
    ckbd = CaribouKeyboard(qwerty)
    window = gtk.Window(gtk.WINDOW_POPUP)
    window.add(ckbd)
    window.show_all()
    gtk.main()
