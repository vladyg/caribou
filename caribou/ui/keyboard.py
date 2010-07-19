# -*- coding: utf-8 -*-
#
# Caribou - text entry and UI navigation application
#
# Copyright (C) 2009 Adaptive Technology Resource Centre
#  * Contributor: Ben Konrath <ben@bagu.org>
# Copyright (C) 2009 Eitan Isaacson <eitan@monotonous.org>
# Copyright (C) 2010 Igalia S.L.
#  * Contributor: Joaquim Rocha <jrocha@igalia.com>
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

import caribou.common.const as const
import gconf
import gobject
import gtk
import sys
import virtkey
import os
try:
    import json
except ImportError:
    HAS_JSON = False
else:
    HAS_JSON = True
import xml.etree.ElementTree as ET
from xml.dom import minidom


class KeyboardPreferences:
    __gtype_name__ = "KeyboardPreferences"

    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file(os.path.join(const.DATA_DIR, "caribou-prefs.ui"))

        self.window = builder.get_object("dialog_prefs")
        self.window.connect("destroy", self.destroy)
        self.window.connect("delete_event", self.destroy)

        close = builder.get_object("button_close")
        close.connect("clicked", self.destroy)

        client = gconf.client_get_default()
        client.add_dir(const.CARIBOU_GCONF, gconf.CLIENT_PRELOAD_NONE)

        layout_combo = builder.get_object("combobox_layout")
        layout_combo.connect("changed", self._on_layout_changed, client)

        normal_color_button = builder.get_object("normal_state_color_button")
        normal_color_string = client.get_string(const.CARIBOU_GCONF +
                                                "/normal_color") or "grey80"
        normal_color = gtk.gdk.Color(normal_color_string)
        normal_color_button.set_color(normal_color)
        normal_color_button.connect("color-set",
                                    self._on_normal_state_color_set,
                                    client)

        mouse_over_color_button = builder.get_object("mouse_over_color_button")
        mouse_over_color_string = client.get_string(const.CARIBOU_GCONF +
                                                    "/mouse_over") or "yellow"
        mouse_over_color = gtk.gdk.Color(mouse_over_color_string)
        mouse_over_color_button.set_color(mouse_over_color)
        mouse_over_color_button.connect("color-set",
                                        self._on_mouse_over_color_set, 
                                        client)
        
        kbds = self._fetch_keyboards()
        for kbddef in kbds:
            layout_combo.append_text(kbddef)

        defaultkbd = client.get_string(const.CARIBOU_GCONF + "/layout")
        try:
            index = kbds.index(defaultkbd)
        except ValueError:
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

    def _fetch_keyboards(self):
        files = os.listdir(const.KEYBOARDS_DIR)
        kbds = []
        for f in files:
            if (HAS_JSON and f.endswith('.json')) or f.endswith('.xml'):
                module = f.rsplit('.', 1)[0]
                # TODO: verify keyboard before adding it to the list
                kbds.append(module)
        return kbds

    def _on_layout_changed(self, combobox, client):
        kbdname = combobox.get_active_text()
        if kbdname:
            client.set_string("/apps/caribou/osk/layout", kbdname)

    def _on_normal_state_color_set(self, colorbutton, client):
        color = colorbutton.get_color().to_string()
        client.set_string(const.CARIBOU_GCONF + "/normal_color", color)

    def _on_mouse_over_color_set(self, colorbutton, client):
        color = colorbutton.get_color().to_string()
        client.set_string(const.CARIBOU_GCONF + "/mouse_over_color", color)


class Key(gtk.Button):

    def __init__(self, label = '', value = '', key_type = 'normal',
                 width = 1, fill = False):
        super(Key, self).__init__()
        self.key_type = key_type
        self.value = value
        self.width = float(width)
        self.fill = False
        self.label = label or value
        if self.key_type == const.DUMMY_KEY_TYPE:
            self.set_relief(gtk.RELIEF_NONE)
            self.set_sensitive(False)
        elif self.key_type == const.PREFERENCES_KEY_TYPE:
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

    def set_color(self, normal_color, mouse_over_color):
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(normal_color))
        self.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.Color(mouse_over_color))

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        if self.key_type == const.NORMAL_KEY_TYPE:
            if type(value) == str or type(value) == unicode:
                value = value.decode('utf-8')
                if len(value) == 1:
                    self._value = gtk.gdk.unicode_to_keyval(ord(value))
                else:
                    key_value = gtk.gdk.keyval_from_name(value)
                    if key_value:
                        self._value = key_value
        elif self.key_type == const.MASK_KEY_TYPE:
            if type(value) == str or type(value) == unicode:
                for key, mask in const.KEY_MASKS.items():
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

class KbLayoutDeserializer(object):

    def __init__(self):
        pass

    def deserialize(self, kb_layout_file):
        kb_file = os.path.abspath(kb_layout_file)
        if not os.path.isfile(kb_file):
            return []
        kb_file_obj = open(kb_file)
        contents = kb_file_obj.read()
        kb_file_obj.close()
        basename, ext = os.path.splitext(kb_file)
        try:
            kb_layouts = self._deserialize_from_format(ext, contents)
        except:
            pass
        else:
            return kb_layouts
        return []

    def _deserialize_from_format(self, format, contents):
        if format == '.xml':
            return self._deserialize_from_xml(contents)
        if HAS_JSON and format == '.json':
            return self._deserialize_from_json(contents)
        return []

    def _deserialize_from_json(self, contents):
        contents_dict = json.loads(contents)
        layouts = self._create_kb_layout_from_dict(contents_dict)
        return layouts

    def _convert_xml_to_dict(self, element):
        if element.text and element.text.strip():
            return element.text
        attributes = element.attrib
        for child in element.getchildren():
            if attributes.get(child.tag):
                attributes[child.tag] += [self._convert_xml_to_dict(child)]
            else:
                attributes[child.tag] = [self._convert_xml_to_dict(child)]
        for key, value in attributes.items():
            if isinstance(value, list) and len(value) == 1:
                attributes[key] = value[0]
        return attributes

    def _deserialize_from_xml(self, xml_string):
        element = ET.fromstring(xml_string)
        layout_dict = self._convert_xml_to_dict(element)
        return self._create_kb_layout_from_dict(layout_dict)

    def _create_kb_layout_from_dict(self, dictionary):
        if not isinstance(dictionary, dict):
            return None
        layouts = self._get_dict_value_as_list(dictionary, 'layout')
        layouts_encoded = []
        for layout in layouts:
            name = layout.get('name')
            if not name:
                continue
            kb_layout = KeyboardLayout(name)
            rows_list = self._get_dict_value_as_list(layout, 'rows')
            for rows in rows_list:
                for row_encoded in self._get_rows_from_dict(rows):
                    kb_layout.add_row(row_encoded)
                layouts_encoded.append(kb_layout)
        return layouts_encoded

    def _get_rows_from_dict(self, rows):
        rows_encoded = []
        row_list = self._get_dict_value_as_list(rows, 'row')
        for row in row_list:
            keys = self._get_dict_value_as_list(row, 'key')
            if keys:
                rows_encoded.append(self._get_keys_from_list(keys))
        return rows_encoded

    def _get_keys_from_list(self, keys_list):
        keys = []
        for key_vars in keys_list:
            vars = {}
            for key, value in key_vars.items():
                vars[str(key)] = value
            key = Key(**vars)
            keys.append(key)
        return keys

    def _get_dict_value_as_list(self, dictionary, key):
        if isinstance(dictionary, list):
            return dictionary
        value = dictionary.get(key)
        if not value:
            return None
        if isinstance(value, list):
            return value
        return [value]

class CaribouKeyboard(gtk.Notebook):
    __gtype_name__ = "CaribouKeyboard"

    def __init__(self):
        gtk.Notebook.__init__(self)
        self.set_show_tabs(False)
        self.vk = virtkey.virtkey()
        self.key_size = 30
        self.current_mask = 0
        self.current_page = 0
        self.client = gconf.client_get_default()

        self.client.notify_add(const.CARIBOU_GCONF + "/normal_color",
                               self._colors_changed)
        self.client.notify_add(const.CARIBOU_GCONF + "/mouse_over_color",
                               self._colors_changed)

    def load_kb(self, kb_location):
        kb_deserializer = KbLayoutDeserializer()
        layouts = kb_deserializer.deserialize(kb_location)
        self._set_layouts(layouts)
        self._update_colors()

    def _set_layouts(self, layout_list):
        self._clear()
        for layout in layout_list:
            self.append_page(layout)
            for row in layout.rows:
                for key in row:
                    if key.key_type == const.LAYOUT_SWITCHER_KEY_TYPE:
                        key.connect('clicked',
                                    self._pressed_layout_switcher_key)
                    elif key.key_type == const.MASK_KEY_TYPE:
                        key.connect('clicked',
                                    self._pressed_mask_key)
                    elif key.key_type == const.PREFERENCES_KEY_TYPE:
                        key.connect('clicked',
                                    self._pressed_preferences_key)
                    else:
                        key.connect('clicked',
                                    self._pressed_normal_key)
                    key.set_relative_size(self.key_size)

    def _colors_changed(self, client, connection_id, entry, args):
        self._update_colors()

    def _update_colors(self):
        normal_color = self.client.get_string(const.CARIBOU_GCONF +
                                              "/normal_color") or "grey80"
        mouse_over_color = self.client.get_string(const.CARIBOU_GCONF +
                                                  "/mouse_over_color") or \
                                                  "yellow"
        n_pages = self.get_n_pages()
        for i in range(n_pages):
            layout = self.get_nth_page(i)
            for row in layout.rows:
                for button in row:
                    button.set_color(normal_color,
                                     mouse_over_color)

    def _clear(self):
        n_pages = self.get_n_pages()
        for i in range(n_pages):
            self.remove_page(i)

    def _pressed_normal_key(self, key):
        self.vk.press_keysym(key.value)
        self.vk.release_keysym(key.value)
        self.current_mask = 0

    def _pressed_layout_switcher_key(self, key):
        self._switch_to_layout(key.value)

    def _pressed_mask_key(self, key):
        if self.current_mask & key.value != 0:
            self.vk.unlatch_mod(key.value)
            self.current_mask &= ~key.value
        else:
            self.current_mask |= key.value
            self.vk.latch_mod(self.current_mask)

    def show_all(self):
        self.set_current_page(self.current_page)
        gtk.Notebook.show_all(self)

    def _pressed_preferences_key(self, key):
        KeyboardPreferences()

    def _switch_to_layout(self, name):
        n_pages = self.get_n_pages()
        for i in range(n_pages):
            if self.get_nth_page(i).layout_name == name:
                self.set_current_page(i)
                self.current_page = i
                break
