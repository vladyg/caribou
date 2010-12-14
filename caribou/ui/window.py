# -*- coding: utf-8 -*-
#
# Caribou - text entry and UI navigation application
#
# Copyright (C) 2009 Eitan Isaacson <eitan@monotonous.org>
# Copyright (C) 2010 Warp Networks S.L.
#  * Contributor: Daniel Baeyens <dbaeyens@warp.es>
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

import animation
from caribou import data_path
from gi.repository import GConf
from gi.repository import Gtk
from gi.repository import Gdk
import opacity
import os
import sys
import gobject

CARIBOU_GCONF_LAYOUT_KEY = '/apps/caribou/osk/layout'
CARIBOU_LAYOUT_DIR = 'keyboards'

class CaribouWindow(Gtk.Window):
    __gtype_name__ = "CaribouWindow"
    def __init__(self, text_entry_mech, default_placement=None,
                 min_alpha=1.0, max_alpha=1.0, max_distance=100):
        gobject.GObject.__init__(self, type=Gtk.WindowType.POPUP)

        self.set_name("CaribouWindow")

        self._vbox = Gtk.VBox()
        self.add(self._vbox)
        self.keyboard = text_entry_mech
        self._vbox.pack_start(text_entry_mech, True, True, 0)

        self.connect("size-allocate", lambda w, a: self._update_position())
        self._gconf_client = GConf.Client.get_default()

        self._cursor_location = Rectangle()
        self._entry_location = Rectangle()
        self._default_placement = default_placement or \
            CaribouWindowPlacement()

        conf_file_path = self._get_keyboard_conf()
        if conf_file_path:
            text_entry_mech.load_kb(conf_file_path)

        self.connect('show', self._on_window_show)

    def destroy(self):
        self.keyboard.destroy()
        super(Gtk.Window, self).destroy()


    def set_cursor_location(self, cursor_location):
        self._cursor_location = cursor_location
        self._update_position()

    def set_entry_location(self, entry_location):
        self._entry_location = entry_location
        self._update_position()

    def set_default_placement(self, default_placement):
        self._default_placement = default_placement
        self._update_position()

    def _get_root_bbox(self):
        root_window = Gdk.get_default_root_window()
        args = root_window.get_geometry()

        root_bbox = Rectangle(*args)

        current_screen = Gdk.Screen.get_default().get_number()
        for panel in self._gconf_client.all_dirs('/apps/panel/toplevels'):
            orientation = self._gconf_client.get_string(panel+'/orientation')
            size = self._gconf_client.get_int(panel+'/size')
            screen = self._gconf_client.get_int(panel+'/screen')
            if screen != current_screen:
                continue
            if orientation == 'top':
                root_bbox.y += size
                root_bbox.height -= size
            elif orientation == 'bottom':
                root_bbox.height -= size
            elif orientation == 'right':
                root_bbox.x += size
                root_bbox.width -= size
            elif orientation == 'left':
                root_bbox.x -= size
        
        return root_bbox

    def _calculate_position(self, placement=None):
        root_bbox = self._get_root_bbox()
        placement = placement or self._default_placement

        x = self._calculate_axis(placement.x, root_bbox)
        y = self._calculate_axis(placement.y, root_bbox)

        return x, y

    def _update_position(self):
        x, y = self._calculate_position()
        root_bbox = self._get_root_bbox()
        proposed_position = Rectangle(x, y, self.get_allocated_width(),
                                      self.get_allocated_height())
        
        x += self._default_placement.x.adjust_to_bounds(root_bbox, proposed_position)
        y += self._default_placement.y.adjust_to_bounds(root_bbox, proposed_position)
        self.move(x, y)

    def _calculate_axis(self, axis_placement, root_bbox):
        bbox = root_bbox

        if axis_placement.stickto == CaribouWindowPlacement.CURSOR:
            bbox = self._cursor_location
        elif axis_placement.stickto == CaribouWindowPlacement.ENTRY:
            bbox = self._entry_location

        offset = axis_placement.get_offset(bbox.x, bbox.y)

        if axis_placement.align == CaribouWindowPlacement.END:
            offset += axis_placement.get_length(bbox.width, bbox.height)
            if axis_placement.gravitate == CaribouWindowPlacement.INSIDE:
                offset -= axis_placement.get_length(
                    self.get_allocated_width(),
                    self.get_allocated_height())
        elif axis_placement.align == CaribouWindowPlacement.START:
            if axis_placement.gravitate == CaribouWindowPlacement.OUTSIDE:
                offset -= axis_placement.get_length(
                    self.get_allocated_width(),
                    self.get_allocated_height())
        elif axis_placement.align == CaribouWindowPlacement.CENTER:
            offset += axis_placement.get_length(bbox.width, bbox.height)/2

        return offset

    def _get_keyboard_conf(self):
        layout = self._gconf_client.get_string(CARIBOU_GCONF_LAYOUT_KEY) \
            or "qwerty"
        conf_file_path = os.path.join(data_path, CARIBOU_LAYOUT_DIR, layout)

        if os.path.exists(conf_file_path):
            return conf_file_path
        else:
            json_path = '%s.json' % conf_file_path

            if os.path.exists(json_path):
                return json_path

            xml_path = '%s.xml' % conf_file_path

            if os.path.exists(xml_path):
                return xml_path


    def show_all(self):
        Gtk.Window.show_all(self)
        self.keyboard.show_all()

    def hide(self):
        self.keyboard.hide()
        Gtk.Window.hide(self)

    def _on_window_show(self, window):
        child = self.get_child()
        border = self.get_border_width()
        req = child.size_request()
        self.resize(req.width + border, req.height + border)

class CaribouWindowDocked(CaribouWindow, 
                          animation.AnimatedWindowBase,
                          opacity.ProximityWindowBase):
    __gtype_name__ = "CaribouWindowDocked"
    
    def __init__(self, text_entry_mech):
        placement = CaribouWindowPlacement(
            xalign=CaribouWindowPlacement.END,
            yalign=CaribouWindowPlacement.START,
            xstickto=CaribouWindowPlacement.SCREEN,
            ystickto=CaribouWindowPlacement.SCREEN,
            xgravitate=CaribouWindowPlacement.INSIDE)

        CaribouWindow.__init__(self, text_entry_mech, placement)
        animation.AnimatedWindowBase.__init__(self)
        opacity.ProximityWindowBase.__init__(
            self, min_alpha=0.5, max_alpha=0.8)

        self.connect('map-event', self.__onmapped)

    def __onmapped(self, obj, event):
        self._roll_in()

    def _roll_in(self):
        x, y = self.get_position()
        self.move(x + self.allocation.width, y)
        #return self.animated_move(x, y)

    def _roll_out(self):
        x, y = self.get_position()
        #return self.animated_move(x + self.allocation.width, y)

    def hide(self):
        animation = self._roll_out()
        animation.connect('completed', lambda x: CaribouWindow.hide(self)) 

class CaribouWindowEntry(CaribouWindow):
    __gtype_name__ = "CaribouWindowEntry"

    def __init__(self, text_entry_mech):
        placement = CaribouWindowPlacement(
            xalign=CaribouWindowPlacement.START,
            xstickto=CaribouWindowPlacement.ENTRY,
            ystickto=CaribouWindowPlacement.ENTRY,
            xgravitate=CaribouWindowPlacement.INSIDE,
            ygravitate=CaribouWindowPlacement.OUTSIDE)

        CaribouWindow.__init__(self, text_entry_mech, placement, min_alpha=0.075,
                               max_alpha=0.8)


    def _calculate_axis(self, axis_placement, root_bbox):
        offset = CaribouWindow._calculate_axis(self, axis_placement, root_bbox)
        if axis_placement.axis == 'y':
            if offset + self.get_allocated_height() > root_bbox.height + root_bbox.y:
                new_axis_placement = axis_placement.copy(align=CaribouWindowPlacement.START)
                offset = CaribouWindow._calculate_axis(self, new_axis_placement, root_bbox)

        return offset

class CaribouWindowPlacement(object):
    START = 'start'
    END = 'end'
    CENTER = 'center'

    SCREEN = 'screen'
    ENTRY = 'entry'
    CURSOR = 'cursor'

    INSIDE = 'inside'
    OUTSIDE = 'outside'

    class _AxisPlacement(object):
        def __init__(self, axis, align, stickto, gravitate):
            self.axis = axis
            self.align = align
            self.stickto = stickto
            self.gravitate = gravitate

        def copy(self, align=None, stickto=None, gravitate=None):
            return self.__class__(self.axis,
                                  align or self.align,
                                  stickto or self.stickto,
                                  gravitate or self.gravitate)

        def get_offset(self, x, y):
            return x if self.axis == 'x' else y

        def get_length(self, width, height):
            return width if self.axis == 'x' else height

        def adjust_to_bounds(self, root_bbox, child_bbox):
            child_vector_start = self.get_offset(child_bbox.x, child_bbox.y)
            child_vector_end = \
                self.get_length(child_bbox.width, child_bbox.height) + \
                child_vector_start
            root_vector_start = self.get_offset(root_bbox.x, root_bbox.y)
            root_vector_end = self.get_length(
                root_bbox.width, root_bbox.height) + root_vector_start

            if root_vector_end < child_vector_end:
                return root_vector_end - child_vector_end

            if root_vector_start > child_vector_start:
                return root_vector_start - child_vector_start

            return 0


    def __init__(self,
                 xalign=None, xstickto=None, xgravitate=None,
                 yalign=None, ystickto=None, ygravitate=None):
        self.x = self._AxisPlacement('x',
                                     xalign or self.END,
                                     xstickto or self.CURSOR,
                                     xgravitate or self.OUTSIDE)
        self.y = self._AxisPlacement('y',
                                     yalign or self.END,
                                     ystickto or self.CURSOR,
                                     ygravitate or self.OUTSIDE)


class Rectangle(object):
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

if __name__ == "__main__":
    import keyboard
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    w = CaribouWindowDocked(keyboard.CaribouKeyboard)
    w.show_all()

    try:
        Gtk.main()
    except KeyboardInterrupt:
        Gtk.main_quit()
