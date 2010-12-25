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
import scan
from preferences_window import PreferencesWindow
import gconf
import gobject
import gtk
import pango
import sys
import virtkey
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

class BaseKey(object):
    '''An abstract class the represents a key on the keyboard.
    Inheriting classes also need to inherit from gtk.Button or any
    of it's subclasses.'''

    def __init__(self, label = '', value = '', key_type = 'normal',
                 width = 1, fill = False):
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

        self.connect('size-allocate', self._on_size_allocate)

    def _on_size_allocate(self, widget, allocation):
        widget.set_property('width-request', allocation.height * self.width)

    def set_font(self, font):
        label = self.get_child()
        if not isinstance(label, gtk.Label):
            return
        rcstyle = label.get_modifier_style()
        rcstyle.font_desc = pango.FontDescription(font)

        label.modify_style(rcstyle)
        label.queue_resize()

    def reset_font(self):
        label = self.get_child()
        if not isinstance(label, gtk.Label):
            return
        rcstyle = label.get_modifier_style()
        rcstyle.font_desc = None
        label.modify_style(rcstyle)
        label.queue_resize()

    def set_color(self, normal_color, mouse_over_color):
        rcstyle = self.get_modifier_style()

        rcstyle.bg[gtk.STATE_NORMAL] = gtk.gdk.Color(normal_color)
        rcstyle.bg[gtk.STATE_PRELIGHT] = gtk.gdk.Color(mouse_over_color)

        self.modify_style(rcstyle)

    def reset_color(self):
        rcstyle = self.get_modifier_style()
        rcstyle.bg[gtk.STATE_NORMAL] = None
        rcstyle.bg[gtk.STATE_PRELIGHT] = None
        self.modify_style(rcstyle)

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
                for key, mask in KEY_MASKS.items():
                    if value == key:
                        self._value = mask
        else:
            self._value = value

    value = property(_get_value, _set_value)

class Key(gtk.Button, BaseKey):
    def __init__(self, label = '', value = '', key_type = 'normal',
                 width = 1, fill = False):
        gtk.Button.__init__(self)
        BaseKey.__init__(self, label, value, key_type, width, fill)

class ModifierKey(gtk.ToggleButton, BaseKey):
    def __init__(self, label = '', value = '', key_type = 'normal',
                 width = 1, fill = False):
        gtk.ToggleButton.__init__(self)
        BaseKey.__init__(self, label, value, key_type, width, fill)

class KeyboardLayout(gtk.Alignment):
    def __init__(self, name):
        super(KeyboardLayout, self).__init__(0, 0, 0, 0)
        self.layout_name = name
        self.rows = []
        self.vbox = gtk.VBox()
        self.vbox.set_homogeneous(True)
        self.add(self.vbox)

    def add_row(self, row):
        self.rows.append(row)
        alignment = gtk.Alignment(0.5, 0.5, 1, 1)
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

class CaribouKeyboard(gtk.Notebook):
    __gtype_name__ = "CaribouKeyboard"

    def __init__(self):
        gtk.Notebook.__init__(self)
        self.set_show_tabs(False)
        self.vk = virtkey.virtkey()
        self.key_size = 30
        self.current_mask = 0
        self.current_page = 0

        # Settings we care about.
        for name in ["normal_color", "mouse_over_color", "default_colors"]:
            getattr(SettingsManager, name).connect("value-changed",
                                                   self._colors_changed)

        for name in ["default_font", "key_font"]:
            getattr(SettingsManager, name).connect("value-changed",
                                         self._key_font_changed)

        self.scan_enabled = SettingsManager.scan_enabled
        
        self.scan_enabled.connect("value-changed",
                                  self._scan_enabled)

        self.scan_service = None

        self.connect('size-allocate', self._on_size_allocate)

        self.row_height = -1

    def reset_row_height(self):
        for i in xrange(self.get_n_pages()):
            layout = self.get_nth_page(i)
            for row in layout.vbox.get_children():
                row.set_property('height-request', -1)
        self.row_height = -1

    def _on_size_allocate(self, notebook, allocation):
        if self.row_height > 0:
            return

        for i in xrange(self.get_n_pages()):
            layout = self.get_nth_page(i)
            rows = layout.vbox.get_children()
            height = rows[0].allocation.height
            self.row_height = max(self.row_height, height)
        for i in xrange(self.get_n_pages()):
            layout = self.get_nth_page(i)
            for row in layout.vbox.get_children():
                row.set_property('height-request', self.row_height)
        

    def load_kb(self, kb_location):
        kb_deserializer = KbLayoutDeserializer()
        layouts = kb_deserializer.deserialize(kb_location)
        self._set_layouts(layouts)
        self._update_key_style()
        self._enable_scanning()

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
                        key.connect('toggled',
                                    self._toggled_mask_key)
                    elif key.key_type == const.PREFERENCES_KEY_TYPE:
                        key.connect('clicked',
                                    self._pressed_preferences_key)
                    else:
                        key.connect('clicked',
                                    self._pressed_normal_key)

    def _scan_enabled(self, setting, val):
        self._enable_scanning()

    def _colors_changed(self, setting, val):
        self._update_key_style()

    def _key_font_changed(self, setting, val):
        self.reset_row_height()
        self._update_key_style()

    def _update_key_style(self):
        default_colors = SettingsManager.default_colors.value
        normal_color = SettingsManager.normal_color.value
        mouse_over_color = SettingsManager.mouse_over_color.value
        default_font = SettingsManager.default_font.value
        key_font = SettingsManager.key_font.value

        n_pages = self.get_n_pages()
        for i in range(n_pages):
            layout = self.get_nth_page(i)
            for row in layout.rows:
                for button in row:
                    if default_colors:
                        button.reset_color()
                    else:
                        button.set_color(normal_color,
                                         mouse_over_color)
                    if default_font:
                        button.reset_font()
                    else:
                        button.set_font(key_font)

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

    def _toggled_mask_key(self, key):
        if not key.get_active():
            self.vk.unlatch_mod(key.value)
            self.current_mask &= ~key.value
        else:
            self.current_mask |= key.value
            self.vk.latch_mod(self.current_mask)

    def show_all(self):
        self.set_current_page(self.current_page)
        gtk.Notebook.show_all(self)
        #if self.scan_enabled.value:
        #    self.scan_service.start()

    def _pressed_preferences_key(self, key):
        p = PreferencesWindow()
        p.show_all()
        p.run()
        p.destroy()

    def _enable_scanning(self):
        if self.scan_enabled.value and self.scan_service is None:
            current_layout = self.get_nth_page(self.current_page)
            self.scan_service = scan.ScanService(
                current_layout.rows, 
                self.get_parent().get_parent())

    def destroy(self):
        if self.scan_enabled.value:
            self.scan_service.destroy()
        for id in self._gconf_connections:
            self.client.notify_remove(id)
        super(gtk.Notebook, self).destroy()

    def _switch_to_layout(self, name):
        n_pages = self.get_n_pages()
        for i in range(n_pages):
            if self.get_nth_page(i).layout_name == name:
                self.set_current_page(i)
                self.current_page = i
                if self.scan_enabled.value:
                    self.scan_service.change_keyboard(
                            self.get_nth_page(i).rows)
                break
