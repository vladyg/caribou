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

import gtk, glib
from math import sqrt

class ProximityWindowBase(object):
    def __init__(self, min_alpha=1.0, max_alpha=1.0, max_distance=100):
        if self.__class__ == ProximityWindowBase:
            raise TypeError, \
                "ProximityWindowBase is an abstract class, " \
                "must be subclassed with a gtk.Window"
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
        x, y = self.get_pointer()
        
        distance =  self._get_distance_to_bbox(x, y, self.allocation)

        opacity = (self.max_alpha - self.min_alpha) * \
            (1 - min(distance, self.max_distance)/self.max_distance)
        opacity += self.min_alpha

        self.set_opacity(opacity)
        return self.props.visible

    def _get_distance_to_bbox(self, x, y, bbox):
        if x < bbox.x:
            x_distance = bbox.x - x
        elif x > bbox.width + bbox.x:
            x_distance = bbox.width + bbox.x - x
        else:
            x_distance = 0

        if y < bbox.y:
            y_distance = bbox.y - y
        elif y > bbox.height + bbox.y:
            y_distance = bbox.height + bbox.y - y
        else:
            y_distance = 0

        if y_distance == 0 and x_distance == 0:
            return 0.0
        elif y_distance != 0 and x_distance == 0:
            return abs(float(y_distance))
        elif y_distance == 0 and x_distance != 0:
            return abs(float(x_distance))
        else:
            x2 = bbox.x if x_distance > 0 else bbox.x + bbox.width
            y2 = bbox.y if y_distance > 0 else bbox.y + bbox.height
            return sqrt((x - x2)**2 + (y - y2)**2)
