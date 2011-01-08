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

import glib
from math import sqrt

class ProximityWindowBase(object):
    def __init__(self, min_alpha=1.0, max_alpha=1.0, max_distance=100):
        if self.__class__ == ProximityWindowBase:
            raise TypeError, \
                "ProximityWindowBase is an abstract class, " \
                "must be subclassed with a Gtk.Window"
        self.connect('map-event', self.__onmapped)
        self.max_distance = max_distance
        if max_alpha < min_alpha:
            raise ValueError, "min_alpha can't be larger than max_alpha"
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha

    def __onmapped(self, obj, event):
        if self.is_composited():
            self.set_opacity(self.max_alpha)
            if self.max_alpha != self.min_alpha:
                # Don't waste CPU if the max and min are equal.
                glib.timeout_add(80, self._proximity_check)

    def _proximity_check(self):
        px, py = self.get_pointer()

        ww = self.get_allocated_width()
        wh = self.get_allocated_height()

        distance =  self._get_distance_to_bbox(px, py, ww, wh)

        opacity = (self.max_alpha - self.min_alpha) * \
            (1 - min(distance, self.max_distance)/self.max_distance)
        opacity += self.min_alpha

        self.set_opacity(opacity)
        return self.props.visible

    def _get_distance_to_bbox(self, px, py, bw, bh):
        if px < 0:
            x_distance = float(abs(px))
        elif px > bw:
            x_distance = float(px - bw)
        else:
            x_distance = 0.0

        if py < 0:
            y_distance = float(abs(px))
        elif py > bh:
            y_distance = float(py - bh)
        else:
            y_distance = 0.0

        if y_distance == 0 and x_distance == 0:
            return 0.0
        elif y_distance != 0 and x_distance == 0:
            return y_distance
        elif y_distance == 0 and x_distance != 0:
            return x_distance
        else:
            x2 = 0 if x_distance > 0 else bw
            y2 = 0 if y_distance > 0 else bh
            return sqrt((px - x2)**2 + (py - y2)**2)
