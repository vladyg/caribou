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
import os

import keyboards
from . import data_path

NORMAL_KEY_TYPE = 'normal'
LAYOUT_SWITCHER_KEY_TYPE = 'layout_switcher'
PREFERENCES_KEY_TYPE = 'preferences'
DUMMY_KEY_TYPE = 'dummy'
MASK_KEY_TYPE = 'mask'

KEY_MASKS = {'shift': gtk.gdk.SHIFT_MASK,
             'lock': gtk.gdk.LOCK_MASK,
             'control': gtk.gdk.CONTROL_MASK,
             'mod1': gtk.gdk.MOD1_MASK,
             'mod2': gtk.gdk.MOD2_MASK,
             'mod3': gtk.gdk.MOD3_MASK,
             'mod4': gtk.gdk.MOD4_MASK,
             'mod5': gtk.gdk.MOD5_MASK,
             'button1': gtk.gdk.BUTTON1_MASK,
             'button2': gtk.gdk.BUTTON2_MASK,
             'button3': gtk.gdk.BUTTON3_MASK,
             'button4': gtk.gdk.BUTTON4_MASK,
             'button5': gtk.gdk.BUTTON5_MASK}


class KeyboardPreferences:
    __gtype_name__ = "KeyboardPreferences"

    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file(os.path.join(data_path, "caribou-prefs.ui"))

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

class Key(gtk.Button):

    def __init__(self, label = '', value = '', key_type = 'normal',
                 width = 1, fill = False):
        super(Key, self).__init__()
        self.key_type = key_type
        self.value = value
        self.width = float(width)
        self.fill = False
        self.label = label or value
        if self.key_type == DUMMY_KEY_TYPE:
            self.set_relief(gtk.RELIEF_NONE)
            self.set_sensitive(False)
        elif self.key_type == PREFERENCES_KEY_TYPE:
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_PREFERENCES,
                                 gtk.ICON_SIZE_BUTTON)
            self.set_image(image)
        else:
            if label:
                label_markup = gtk.Label()
                label_markup.set_markup(self.label)
                self.add(label_markup)
            else:
                self.set_label(self.label)

    def set_relative_size(self, size):
        self.set_size_request(int(size * self.width), int(size))

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        if self.key_type == NORMAL_KEY_TYPE:
            if type(value) == str or type(value) == unicode:
                value = value.decode('utf-8')
                if len(value) == 1:
                    self._value = ord(value)
                else:
                    key_value = gtk.gdk.keyval_from_name(value)
                    if key_value:
                        self._value = key_value
        elif self.key_type == MASK_KEY_TYPE:
            if type(value) == str or type(value) == unicode:
                for key, mask in KEY_MASKS.items():
                    if value == key:
                        self._value = mask
        else:
            self._value = value

    value = property(_get_value, _set_value)

class KeyboardLayout(gtk.Alignment):

    def __init__(self, name):
        super(KeyboardLayout, self).__init__(0, 0, 0, 0)
        self.layout_name = name
        self.rows = []
        self.vbox = gtk.VBox()
        self.add(self.vbox)

    def add_row(self, row):
        self.rows.append(row)
        alignment = gtk.Alignment(0.5, 0.5, 0, 0)
        hbox = gtk.HBox()
        for key in row:
            hbox.pack_start(key, expand = True, fill = key.fill)
        alignment.add(hbox)
        self.vbox.pack_start(alignment)



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
