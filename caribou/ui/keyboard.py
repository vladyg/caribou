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
from caribou import data_path
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

PRETTY_LABELS = {
    "BackSpace" : u'\u232b',
    "space" : u' ',
    "Return" : u'\u23ce',
    'Caribou_Prefs' : u'\u2328',
    'Caribou_ShiftUp' : u'\u2b06',
    'Caribou_ShiftDown' : u'\u2b07',
    'Caribou_Emoticons' : u'\u263a',
    'Caribou_Symbols' : u'123',
    'Caribou_Symbols_More' : u'{#*',
    'Caribou_Alpha' : u'Abc'
}

class BaseKey(object):
    '''An abstract class the represents a key on the keyboard.
    Inheriting classes also need to inherit from Gtk.Button or any
    of it's subclasses.'''

    def __init__(self, **kwargs):
        if not kwargs.has_key("name"):
            raise TypeError, "%r requires a 'name' parameter" % self.__class__
        self.margin_left = 0
        self.width = 1

        for k, v in kwargs.items():
            setattr(self, k, v)
        if hasattr(self, "extended_names"):
            self.extended_keys = \
                [self.__class__(name=n) for n in [self.name] + self.extended_names]
        else:
            self.extended_keys = []

        self.keyval, self.key_label = self._get_keyval_and_label(self.name)
        self.set_label(self.key_label)

        ctx = self.get_style_context()
        ctx.add_class("caribou-keyboard-button")

        for name in ["default_font", "key_font"]:
            getattr(SettingsManager, name).connect("value-changed",
                                         self._key_font_changed)

        if not SettingsManager.default_font.value:
            self._key_font_changed(None, None)

    def _get_keyval_and_label(self, name):
        keyval = Gdk.keyval_from_name(name)
        if PRETTY_LABELS.has_key(name):
            label = PRETTY_LABELS[name]
        elif name.startswith('Caribou_'):
            label = name.replace('Caribou_', '')
        else:
            unichar = unichr(Gdk.keyval_to_unicode(keyval))
            if unichar.isspace() or unichar == u'\x00':
                label = name
            else:
                label = unichar

        return keyval, label

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

    def set_font(self, font):
        raise NotImplemented

    def reset_font(self):
        raise NotImplemented

class CaribouSubKeys(Gtk.Window):
    def __init__(self, keys):
        gobject.GObject.__init__(self, type=Gtk.WindowType.POPUP)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_accept_focus(False)
        self.set_position(Gtk.WindowPosition.MOUSE)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)

        for key in keys:
            key.connect("clicked", self._on_key_clicked)

        layout = KeyboardLayout(key.name, "subkeyboard")
        layout.add_row(keys)
        self.add(layout)

    def show_subkeys(self, parent):
        self.set_transient_for(parent)
        self._parent = parent
        self._parent.set_sensitive(False)
        self.show_all()

    def _on_key_clicked(self, key):
        self._parent.set_sensitive(True)
        self.hide()

class Key(Gtk.Button, BaseKey):
    def __init__(self, **kwargs):
        gobject.GObject.__init__(self)
        BaseKey.__init__(self, **kwargs)
        if self.extended_keys:
            self.sub_keys = CaribouSubKeys(self.extended_keys)
        else:
            self.sub_keys = None

        child = self.get_child()
        child.set_padding(4, 4)

    def do_get_preferred_width_for_height(self, w):
        return (w, w)

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.HEIGHT_FOR_WIDTH

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

class KeyboardLayout(Gtk.Grid):
    KEY_SPAN = 4

    def __init__(self, name, mode):
        gobject.GObject.__init__(self)
        self.layout_name = name
        self.mode = mode
        self.rows = []
        self.set_column_homogeneous(True)
        self.set_row_homogeneous(True)
        self.set_row_spacing(4)
        self.set_column_spacing(4)

    def add_row(self, row):
        row_num = len(self.rows)
        self.rows.append(row)
        col_num = 0
        for i, key in enumerate(row):
            self.attach(key,
                        col_num + int(key.margin_left * self.KEY_SPAN),
                        row_num * self.KEY_SPAN,
                        int(self.KEY_SPAN * key.width),
                        self.KEY_SPAN)
            col_num += int((key.width + key.margin_left ) * self.KEY_SPAN)

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
    def _get_layout_file(self, group, variant):
        layout_path = os.path.join(data_path, "layouts",
                                   SettingsManager.geometry.value)
        for fn in ('%s_%s.json' % (group, variant),
                   '%s.json' % group):
            layout_file = os.path.join(layout_path, fn)
            if os.path.exists(layout_file):
                return layout_file
        return None

    def deserialize(self, group, variant):
        kb_file = self._get_layout_file(group, variant)
        if not kb_file:
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
        layouts_encoded = []
        for name, level in dictionary.items():
            kb_layout = KeyboardLayout(name, level.get("mode", "locked"))
            rows_list = self._get_dict_value_as_list(level, 'rows')
            for row in rows_list:
                keys = self._get_keys_from_list(row)
                kb_layout.add_row(keys)
            layouts_encoded.append(kb_layout)
        return layouts_encoded

    def _get_keys_from_list(self, keys_list):
        keys = []
        for key_vars in keys_list:
            vars = {}
            for key, value in key_vars.items():
                vars[str(key)] = value
            if vars.get('modifier', False) == const.MASK_KEY_TYPE:
                key = ModifierKey(self.vk, **vars)
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
        self.layouts = {}
        self._load_kb()
        self.vk.connect('group-changed', self._on_group_changed)
        grpid, group, variant = self.vk.get_current_group()
        self._on_group_changed(self.vk, grpid, group, variant)
        self._key_hold_tid = 0

    def _load_kb(self):
        kb_deserializer = KbLayoutDeserializer()
        groups, variants = self.vk.get_groups()
        for group, variant in zip(groups, variants):
            levels = kb_deserializer.deserialize(group, variant)
            self._add_levels('%s_%s' % (group, variant), levels)

    def _connect_key_signals(self, key):
        if hasattr(key, "toggle"):
            key.connect('clicked',
                        self._pressed_layout_switcher_key)
        elif key.name == "Caribou_Prefs":
            key.connect('clicked', self._pressed_preferences_key)
        elif key.keyval != 0:
            if False: # We should enable this for hardware emulation
                key.connect('pressed',
                            self._pressed_normal_key)
                key.connect('released',
                            self._released_normal_key)
            else:
                key.connect('clicked',
                            self._clicked_normal_key)
                key.connect('pressed',
                            self._key_hold_start)
                key.connect('released',
                            self._key_hold_end)
        

    def _add_levels(self, group, level_list):
        self.layouts[group] = {}
        for level in level_list:
            level.show()
            self.layouts[group][level.layout_name] = self.append_page(level, None)
            if level.mode == "default":
                self.layouts[group]["default"] = \
                    self.layouts[group][level.layout_name]
            for row in level.rows:
                for key in row:
                    self._connect_key_signals(key)
                    for k in key.extended_keys:
                        self._connect_key_signals(k)

    def _clear(self):
        n_pages = self.get_n_pages()
        for i in range(n_pages):
            self.remove_page(i)

    def _key_hold_start(self, key):
        self._key_hold_tid = gobject.timeout_add(1000, self._on_key_held, key)

    def _key_hold_end(self, key):
        if self._key_hold_tid != 0:
            gobject.source_remove(self._key_hold_tid)
            self._key_hold_tid = 0

    def _on_key_held(self, key):
        self._key_hold_tid = 0
        if key.sub_keys:
            key.sub_keys.show_subkeys(self.get_toplevel())
        return False

    def _clicked_normal_key(self, key):
        if self._key_hold_tid == 0:
            return
        self._pressed_normal_key(key)
        self._released_normal_key(key)

    def _pressed_normal_key(self, key):
        self.vk.keyval_press(key.keyval)

    def _released_normal_key(self, key):
        self.vk.keyval_release(key.keyval)
        layout = self.get_nth_page(self.get_current_page())
        if layout.mode == "latched":
            self._switch_to_layout()
        while True:
            try:
                mod = self.depressed_mods.pop()
            except IndexError:
                break
            mod.set_active (False)

    def _pressed_layout_switcher_key(self, key):
        self._switch_to_layout(level=key.toggle)

    def _on_group_changed(self, vk, groupid, group, variant):
        self._switch_to_layout('%s_%s' % (group, variant))

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

    def _switch_to_fallback(self, group):
        try:
            i = min(self.layouts[group].values())
        except KeyError:
            i = 0
        self.set_current_page(i)

    def _switch_to_layout(self, group=None, level="default"):
        if group is None:
            _, _group, _variant = self.vk.get_current_group()
            group = '%s_%s' % (_group, _variant)
        if self.layouts.has_key(group):
            if self.layouts[group].has_key(level):
                self.set_current_page(self.layouts[group][level])
                return
        self._switch_to_fallback(group)

    def get_current_layout(self):
        i = self.get_current_page()
        return self.get_nth_page(i)

    def get_layouts(self):
        return [self.get_nth_page(i) for i in xrange(self.get_n_pages())]

if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    w = Gtk.Window()
    w.set_accept_focus(False)

    kb = CaribouKeyboard()
    w.add(kb)

    w.show_all()

    Gtk.main()
