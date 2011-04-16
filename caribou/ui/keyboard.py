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
from caribou.common.settings_manager import SettingsManager
from preferences_window import PreferencesWindow
from gi.repository import GConf
import gobject
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import Caribou
import sys
import os
import traceback
from caribou.ui.i18n import _
from caribou.common.setting_types import *

try:
    import json
except ImportError:
    HAS_JSON = False
else:
    HAS_JSON = True
import xml.etree.ElementTree as ET
from xml.dom import minidom
import gettext
import i18n

class BaseKey(object):
    '''An abstract class the represents a key on the keyboard.
    Inheriting classes also need to inherit from Gtk.Button or any
    of it's subclasses.'''

    def __init__(self, label = '', value = '', key_type = 'normal',
                 width = 1, fill = False):
        self.key_type = key_type
        self.value = value
        self.width = float(width)
        self.fill = False
        self.label = label or value
        if self.key_type == const.DUMMY_KEY_TYPE:
            self.set_relief(Gtk.ReliefStyle.NONE)
            self.set_sensitive(False)
        elif self.key_type == const.PREFERENCES_KEY_TYPE:
            image = Gtk.Image()
            image.set_from_stock(Gtk.STOCK_PREFERENCES,
                                 Gtk.IconSize.BUTTON)
            self.set_image(image)
        else:
            if label:
                label_markup = Gtk.Label()
                label_markup.set_markup(self.label)
                self.add(label_markup)
            else:
                self.set_label(self.label)

        ctx = self.get_style_context()
        ctx.add_class("caribou-keyboard-button")

        for name in ["default_font", "key_font"]:
            getattr(SettingsManager, name).connect("value-changed",
                                         self._key_font_changed)

        if not SettingsManager.default_font.value:
            self._key_font_changed(None, None)

    def _key_font_changed(self, setting, value):
        if SettingsManager.default_font.value:
            self.reset_font()
        else:
            self.set_font(SettingsManager.key_font.value)

    def scan_highlight_key(self):
        raise NotImplemented

    def scan_highlight_row(self):
        raise NotImplemented

    def scan_highlight_block(self):
        raise NotImplemented

    def scan_highlight_cancel(self):
        raise NotImplemented

    def scan_highlight_clear(self):
        raise NotImplemented

    def _on_image_key_mapped(self, key):
        key_width = key.get_allocated_height()
        icon_size = Gtk.IconSize.MENU
        image = Gtk.Image()
        for size in [Gtk.IconSize.MENU,
                     Gtk.IconSize.SMALL_TOOLBAR,
                     Gtk.IconSize.LARGE_TOOLBAR,
                     Gtk.IconSize.BUTTON,
                     Gtk.IconSize.DND,
                     Gtk.IconSize.DIALOG]:
            pixbuf = image.render_icon_pixbuf(Gtk.STOCK_PREFERENCES, size)
            pixel_size = pixbuf.get_width()
            if pixel_size > key_width:
                break
            icon_size = size
        image.set_from_stock(Gtk.STOCK_PREFERENCES, icon_size)
        self.set_image(image)

    def set_font(self, font):
        raise NotImplemented

    def reset_font(self):
        raise NotImplemented

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        if self.key_type in (const.NORMAL_KEY_TYPE, const.MASK_KEY_TYPE):
            if type(value) == str:
                value = value.decode('utf-8')
            if type(value) == unicode:
                if len(value) == 1:
                    self._value = Gdk.unicode_to_keyval(ord(value))
                else:
                    key_value = Gdk.keyval_from_name(value)
                    if key_value:
                        self._value = key_value
        else:
            self._value = value

    value = property(_get_value, _set_value)

class Key(Gtk.Button, BaseKey):
    def __init__(self, label = '', value = '', key_type = 'normal',
                 width = 1, fill = False):
        gobject.GObject.__init__(self)
        BaseKey.__init__(self, label, value, key_type, width, fill)

    def set_font(self, font):
        child = self.get_child()
        if isinstance(child, Gtk.Label):
            child.modify_font(Pango.font_description_from_string(font))
        if child is not None:
            child.queue_resize()

    def reset_font(self):
        label = self.get_child()
        if not isinstance(label, Gtk.Label):
            return
        label.modify_font(None)

    def _replace_scan_class_style(self, scan_class=None):
        ctx = self.get_style_context()
        for cls in ctx.list_classes():
            if cls.startswith('caribou-scan'):
                ctx.remove_class(cls)
        if scan_class:
            ctx.add_class(scan_class)
        self.queue_draw()

    def scan_highlight_key(self):
        self._replace_scan_class_style("caribou-scan-key")

    def scan_highlight_row(self):
        self._replace_scan_class_style("caribou-scan-row")

    def scan_highlight_block(self):
        self._replace_scan_class_style("caribou-scan-block")

    def scan_highlight_cancel(self):
        self._replace_scan_class_style("caribou-scan-cancel")

    def scan_highlight_clear(self):
        self._replace_scan_class_style()

class ModifierKey(Gtk.ToggleButton, Key):
    pass

class KeyboardLayout(Gtk.Table):
    KEY_SPAN = 4
    def __init__(self, name):
        gobject.GObject.__init__(self)
        self.layout_name = name
        self.rows = []
        self.set_homogeneous(True)

    def add_row(self, row):
        row_num = len(self.rows)
        self.rows.append(row)
        last_col = 0
        for i, key in enumerate(row):
            next_col = (last_col + (key.width * self.KEY_SPAN))
            self.attach(key, last_col, next_col,
                        row_num * self.KEY_SPAN, (row_num + 1) * self.KEY_SPAN,
                        Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL, 
                        Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL,
                        0, 0)
            last_col = next_col
    
    def get_scan_rows(self):
        return [filter(lambda x: x.is_sensitive(), row) for row in self.rows]

    def get_scan_blocks(self, optimal_block_size=8):
        # TODO: smarter division using optimal block size.
        scan_rows = self.get_scan_rows()
        col_num = max([len(row) for row in scan_rows])
        blocks = []
        
        for row_index in xrange(len(scan_rows)):
            for col_index in xrange(max([len(row) for row in scan_rows])):
                try:
                    key = scan_rows[row_index][col_index]
                except IndexError:
                    continue

                try:
                    group = blocks[row_index/2]
                except IndexError:
                    group = []
                    blocks.append(group)
                
                try:
                    group[col_index/3].append(key)
                except IndexError:
                    block = []
                    block.append(key)
                    group.append(block)

        return reduce(lambda a, b: a + b, blocks)
        
                                    

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
        except Exception, e:
            traceback.print_exc()
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
            if vars.get('key_type', '') == const.MASK_KEY_TYPE:
                key = ModifierKey(**vars)
            else:
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

class CaribouKeyboard(Gtk.Notebook):
    __gtype_name__ = "CaribouKeyboard"

    def __init__(self):
        gobject.GObject.__init__(self)
        self.set_show_tabs(False)
        self.vk = Caribou.VirtualKeyboard()
        self.key_size = 30
        self.current_page = 0
        self.depressed_mods = []

        self.row_height = -1

    def load_kb(self, kb_location):
        kb_deserializer = KbLayoutDeserializer()
        layouts = kb_deserializer.deserialize(kb_location)
        self._set_layouts(layouts)

    def _set_layouts(self, layout_list):
        self._clear()            
        for layout in layout_list:
            self.append_page(layout, None)
            for row in layout.rows:
                for key in row:
                    if key.key_type == const.LAYOUT_SWITCHER_KEY_TYPE:
                        key.connect('clicked',
                                    self._pressed_layout_switcher_key)
                    elif key.key_type == const.MASK_KEY_TYPE:
                        key.connect('toggled',
                                    self._toggled_mask_key)
                    elif key.key_type == const.PREFERENCES_KEY_TYPE:
                        key.connect('clicked',
                                    self._pressed_preferences_key)
                    else:
                        key.connect('pressed',
                                    self._pressed_normal_key)
                        key.connect('released',
                                    self._released_normal_key)

    def _clear(self):
        n_pages = self.get_n_pages()
        for i in range(n_pages):
            self.remove_page(i)

    def _pressed_normal_key(self, key):
        self.vk.keyval_press(key.value)

    def _released_normal_key(self, key):
        self.vk.keyval_release(key.value)
        while True:
            try:
                mod = self.depressed_mods.pop()
            except IndexError:
                break
            mod.set_active (False)

    def _pressed_layout_switcher_key(self, key):
        self._switch_to_layout(key.value)

    def _toggled_mask_key(self, key):
        if key.get_active():
            self.vk.keyval_press(key.value)
            self.depressed_mods.append(key)
        else:
            self.vk.keyval_release(key.value)
            try:
                mod = self.depressed_mods.remove(key)
            except ValueError:
                pass

    def show_all_(self):
        self.set_current_page(self.current_page)
        Gtk.Notebook.show_all(self)

    def _pressed_preferences_key(self, key):
        p = PreferencesWindow()
        p.show_all()
        p.run()
        p.destroy()

    def _switch_to_layout(self, name):
        n_pages = self.get_n_pages()
        for i in range(n_pages):
            if self.get_nth_page(i).layout_name == name:
                self.set_current_page(i)
                self.current_page = i
                break

    def get_current_layout(self):
        i = self.get_current_page()
        return self.get_nth_page(i)

    def get_layouts(self):
        return [self.get_nth_page(i) for i in xrange(self.get_n_pages())]

if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    w = Gtk.Window()

    kb = CaribouKeyboard()
    kb.load_kb('data/keyboards/qwerty.xml')

    w.add(kb)

    w.show_all()

    Gtk.main()
