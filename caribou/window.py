# -*- coding: utf-8 -*-
#
# Caribou - text entry and UI navigation application
#
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

import animation
import gconf
import gtk
import gtk.gdk as gdk
import opacity
import os

CARIBOU_GCONF_LAYOUT_KEY = '/apps/caribou/osk/layout'
CARIBOU_LAYOUT_DIR = 'caribou/keyboards'

class CaribouWindow(gtk.Window):
    __gtype_name__ = "CaribouWindow"

    def __init__(self, text_entry_mech, default_placement=None,
                 min_alpha=1.0, max_alpha=1.0, max_distance=100):
        super(CaribouWindow, self).__init__(gtk.WINDOW_POPUP)
        self.set_name("CaribouWindow")

        self._vbox = gtk.VBox()
        self.add(self._vbox)
        self._vbox.pack_start(text_entry_mech)

        self.connect("size-allocate", lambda w, a: self._update_position())
        self._gconf_client = gconf.client_get_default()

        self._cursor_location = gdk.Rectangle()
        self._entry_location = gdk.Rectangle()
        self._default_placement = default_placement or \
            CaribouWindowPlacement()

        conf_file_path = self._get_keyboard_conf()
        if conf_file_path:
            text_entry_mech.load_kb(conf_file_path)

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
        root_window = gdk.get_default_root_window()
        args = root_window.get_position() + root_window.get_size()

        root_bbox = gdk.Rectangle(*args)

        current_screen = gtk.gdk.screen_get_default().get_number()
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
        proposed_position = \
            gdk.Rectangle(x, y, self.allocation.width, self.allocation.height)

        x += self._default_placement.x.adjust_to_bounds(root_bbox, proposed_position)
        y += self._default_placement.y.adjust_to_bounds(root_bbox, proposed_position)
        self.move(x, y)

    def _calculate_axis(self, axis_placement, root_bbox):
        bbox = root_bbox

        if axis_placement.stickto == CaribouWindowPlacement.CURSOR:
            bbox = self._cursor_location
        elif axis_placement.stickto == CaribouWindowPlacement.ENTRY:
            bbox = self._entry_location

        offset = axis_placement.get_offset(bbox)

        if axis_placement.align == CaribouWindowPlacement.END:
            offset += axis_placement.get_length(bbox)
            if axis_placement.gravitate == CaribouWindowPlacement.INSIDE:
                offset -= axis_placement.get_length(self.allocation)
        elif axis_placement.align == CaribouWindowPlacement.START:
            if axis_placement.gravitate == CaribouWindowPlacement.OUTSIDE:
                offset -= axis_placement.get_length(self.allocation)
        elif axis_placement.align == CaribouWindowPlacement.CENTER:
            offset += axis_placement.get_length(bbox)/2

        return offset

    def _get_keyboard_conf(self):
        layout = self._gconf_client.get_string(CARIBOU_GCONF_LAYOUT_KEY)
        conf_file_path = os.path.join(os.curdir,
                                      CARIBOU_LAYOUT_DIR,
                                      layout)
        print conf_file_path
        if os.path.exists(conf_file_path):
            return conf_file_path

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
        return self.animated_move(x, y)

    def _roll_out(self):
        x, y = self.get_position()
        return self.animated_move(x + self.allocation.width, y)

    def hide_all(self):
        animation = self._roll_out()
        animation.connect('completed', lambda x: CaribouWindow.hide_all(self)) 

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
            if offset + self.allocation.height > root_bbox.height + root_bbox.y:
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

        def get_offset(self, bbox):
            return bbox.x if self.axis == 'x' else bbox.y

        def get_length(self, bbox):
            return bbox.width if self.axis == 'x' else bbox.height

        def adjust_to_bounds(self, root_bbox, child_bbox):
            child_vector_start = self.get_offset(child_bbox)
            child_vector_end = self.get_length(child_bbox) + child_vector_start
            root_vector_start = self.get_offset(root_bbox)
            root_vector_end = self.get_length(root_bbox) + root_vector_start

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

