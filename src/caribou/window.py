# -*- coding: utf-8 -*-
#
# Carbou - text entry and UI navigation application
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

import gtk
import gtk.gdk as gdk
import keyboard
from keyboards import qwerty

class CaribouWindow(gtk.Window):
    __gtype_name__ = "CaribouWindow"

    def __init__(self, default_placement=None):
        super(CaribouWindow, self).__init__(gtk.WINDOW_POPUP)
        self.set_name("CaribouWindow")

        self._vbox = gtk.VBox()
        self.add(self._vbox)

        self._vbox.pack_start(keyboard.CaribouKeyboard(qwerty))

        self.connect("size-allocate", lambda w, a: self._update_position())

        self._cursor_location = gdk.Rectangle()
        self._entry_location = gdk.Rectangle()
        self._default_placement = default_placement or \
            CaribouWindowPlacement()

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
        return gdk.Rectangle(*args)

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

class CaribouWindowEntry(CaribouWindow):
    __gtype_name__ = "CaribouWindowEntry"

    def __init__(self):
        placement = CaribouWindowPlacement(
            xalign=CaribouWindowPlacement.START,
            xstickto=CaribouWindowPlacement.ENTRY,
            ystickto=CaribouWindowPlacement.ENTRY,
            xgravitate=CaribouWindowPlacement.INSIDE,
            ygravitate=CaribouWindowPlacement.OUTSIDE)

        CaribouWindow.__init__(self, placement)

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

