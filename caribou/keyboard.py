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

import gconf
import gobject
import gtk
import sys
import virtkey

import keyboards

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

        client = gconf.client_get_default()
        client.add_dir("/apps/caribou/osk", gconf.CLIENT_PRELOAD_NONE)

        layout_combo = builder.get_object("combobox_layout")
        layout_combo.connect("changed", self._on_layout_changed, client)

        for kbddef in keyboards.kbds:
            layout_combo.append_text(kbddef)

        defaultkbd = client.get_string("/apps/caribou/osk/layout")
        try:
            index = keyboards.kbds.index(defaultkbd)
        except ValueError:
            print "FIXME: pick a suitable keyboard layout: " + (defaultkbd or "None")
            layout_combo.set_active(0)
        else:
            layout_combo.set_active(index)

        # grey out the key size, key spacing and test area
        # TODO: implement key size, key spacing and test area
        keysize_label = builder.get_object("label_keysize")
        keysize_label.set_sensitive(False)
        keysize_combo = builder.get_object("combobox_keysize")
        keysize_combo.set_sensitive(False)
        keyspacing_label = builder.get_object("label_keyspacing")
        keyspacing_label.set_sensitive(False)
        keyspacing_combo = builder.get_object("combobox_keyspacing")
        keyspacing_combo.set_sensitive(False)
        test_label = builder.get_object("label_test")
        test_label.set_sensitive(False)
        entry_test = builder.get_object("entry_test")
        entry_test.set_sensitive(False)

        self.window.show_all()

    def destroy(self, widget, data = None):
        self.window.destroy()

    def _on_layout_changed(self, combobox, client):
        kbdname = combobox.get_active_text()
        if kbdname:
            client.set_string("/apps/caribou/osk/layout", kbdname)

class CaribouKeyboard(gtk.Frame):
    __gtype_name__ = "CaribouKeyboard"

    class _KeyboardLayout:
        vk = virtkey.virtkey()

        def __init__(self, kdbdef):
            self.layers, self.switch_layer_buttons = [], []
            for layer in kdbdef.layers:
                layervbox = gtk.VBox(homogeneous = True)
                self.layers.append(layervbox)
                layervbox.set_name(layer)
                # get the layer tuple from the string
                layer = getattr(kdbdef, layer)
                for row in layer:
                    rowhbox = gtk.HBox(homogeneous = True)
                    for key in row:
                        # check if the key is defined by a string or a tuple
                        if isinstance(key, str):
                            if key == "pf":
                                # preferences key
                                button = gtk.Button()
                                button.set_use_underline(False)
                                image = gtk.image_new_from_pixbuf(
                                    button.render_icon(gtk.STOCK_PREFERENCES,
                                                       gtk.ICON_SIZE_BUTTON))
                                button.set_image(image)
                                button.connect("clicked", self._open_prefs)
                            else:
                                # single utf-8 character key
                                button = gtk.Button(key)
                                button.set_use_underline(False)
                                char = ord(key.decode('utf-8'))
                                button.connect("pressed", self._press_cb,
                                               char)
                                button.connect("released", self._release_cb,
                                               char)
                        elif isinstance(key, tuple):
                            button = gtk.Button(key[0])
                            button.set_use_underline(False)
                            # check if this key is a layer switch key or not
                            if isinstance(key[1], str):
                                # switch layer key
                                # set layer name on button and save to process later
                                button.set_name(key[1])
                                self.switch_layer_buttons.append(button)
                            else:
                                # regular key
                                button.connect("pressed",
                                               self._keysym_press_cb, key[1])
                                button.connect("released",
                                               self._keysym_release_cb, key[1])
                        else:
                            pass # TODO: throw error here

                        rowhbox.pack_start(button, expand = False, fill = True)

                    layervbox.pack_start(rowhbox, expand = False, fill = True)

        def _open_prefs(self, widget):
            KeyboardPreferences()

        def _press_cb(self, widget, char):
            self.vk.press_unicode(char)

        def _release_cb(self, widget, char):
            self.vk.release_unicode(char)

        def _keysym_press_cb(self, widget, char):
            self.vk.press_keysym(char)

        def _keysym_release_cb(self, widget, char):
            self.vk.release_keysym(char)

    def __init__(self):
        gtk.Frame.__init__(self)
        self.set_shadow_type(gtk.SHADOW_NONE)

        # FIXME: load from stored value, default to locale appropriate
        kbdloc = "caribou.keyboards.qwerty"
        __import__(kbdloc)
        kbdlayout = self._KeyboardLayout(sys.modules[kbdloc])
        self._set_kbd_layout(kbdlayout)
        # end FIXME

    def _change_layer(self, widget, data):
        self.remove(self.get_child())
        self.add(data)
        self.show_all()

    def _set_kbd_layout(self, layout):
        # FIXME: set kbd name properly
        self._kbd_name = "qwerty"
        # connect the change layer buttons
        for button in layout.switch_layer_buttons:
            for layer in layout.layers:
                if button.get_name() == layer.get_name():
                    button.connect("clicked", self._change_layer, layer)
                    button.set_name("")
                    break
            else:
                print "ERROR" # TODO: throw exception

        # add the first layer and make it visible
        self.add(layout.layers[0])
        self.show_all()

    def get_layout(self):
        return self._kbd_name



if __name__ == "__main__":
    # create test window with keyboard
    # run with: python caribou/keyboard.py
    kbdloc = "keyboards.qwerty"
    __import__(kbdloc)
    ckbd = KeyboardLayout(sys.modules[kbdloc])
    window = gtk.Window(gtk.WINDOW_POPUP)
    window.add(ckbd)
    window.show_all()
    gtk.main()
