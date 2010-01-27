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

import gobject
import gtk
import keyboards
import sys
import virtkey

class KeyboardPreferences:
    __gtype_name__ = "KeyboardPreferences"

    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file("caribou/caribou-prefs.ui")

        self.window = builder.get_object("dialog_prefs")
        self.window.connect("destroy", self.destroy)
        self.window.connect("delete_event", self.destroy)

        close = builder.get_object("button_close")
        close.connect("clicked", self.destroy)

        layout_combo = builder.get_object("combobox_layout")
        # we can't use gtk.combo_box_new_text() with glade
        # we have to manually set up simple combobox
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        layout_combo.set_model(liststore)
        cell = gtk.CellRendererText()
        layout_combo.pack_start(cell, True)
        layout_combo.add_attribute(cell, 'text', 0)

        for kbddef in keyboards.kbds:
            layout_combo.append_text(kbddef)
        layout_combo.set_active(1)

        # grey out the key size and key spacing
        keysize_label = builder.get_object("label_keysize")
        keysize_label.set_sensitive(False)
        keysize_combo = builder.get_object("combobox_keysize")
        keysize_combo.set_sensitive(False)
        keyspacing_label = builder.get_object("label_keyspacing")
        keyspacing_label.set_sensitive(False)
        keyspacing_combo = builder.get_object("combobox_keyspacing")
        keyspacing_combo.set_sensitive(False)

        self.window.show_all()

    def destroy(self, widget, data = None):
        self.window.destroy()

class CaribouKeyboard(gtk.Frame):
    __gtype_name__ = "CaribouKeyboard"

    def __init__(self):
        gtk.Frame.__init__(self)
        self.set_shadow_type(gtk.SHADOW_NONE)

        self._vk = virtkey.virtkey()

        # FIXME: load from stored value, default to locale appropriate
        name = "caribou.keyboards.qwerty"
        #name = "keyboards.qwerty"
        __import__(name)
        kbddef = sys.modules[name]
        # end FIXME

        layouts, switch_buttons = [], []
        for layout in kbddef.layouts:
            layoutvbox = gtk.VBox(homogeneous = True)
            layoutvbox.set_name(layout)
            # get the layout tuple from the string
            layout = getattr(kbddef, layout)
            for row in layout:
                rowhbox = gtk.HBox(homogeneous = True)
                for key in row:
                    # check if the key is defined by a string or a tuple
                    if isinstance(key, str):
                        if key == "pf":
                            # preferences key
                            button = gtk.Button()
                            image = gtk.image_new_from_pixbuf(
                                button.render_icon(gtk.STOCK_PREFERENCES,
                                                   gtk.ICON_SIZE_BUTTON))
                            button.set_image(image)
                            button.connect("clicked", self.__open_prefs)
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

                    rowhbox.pack_start(button, expand = False, fill = True)

                layoutvbox.pack_start(rowhbox, expand = False, fill = True)

            layouts.append(layoutvbox)

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

    def __open_prefs(self, widget):
        prefs = KeyboardPreferences()

if __name__ == "__main__":
    # dynamically import keyboard file
    #name = "keyboards." + keyboards.kbds[0]
    #__import__(name)
    #kbddef = sys.modules[name]

    # create test window with keyboard
    ckbd = CaribouKeyboard()
    window = gtk.Window(gtk.WINDOW_POPUP)
    window.add(ckbd)
    window.show_all()
    gtk.main()
