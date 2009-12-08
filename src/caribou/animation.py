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

import clutter

class AnimatedWindowBase(object):
    def __init__(self, ease=clutter.EASE_IN_QUAD):
        if self.__class__ == AnimatedWindowBase:
            raise TypeError, \
                "AnimatedWindowBase is an abstract class, " \
                "must be subclassed with a gtk.Window"

        self._actor = clutter.Rectangle()
        self.ease = ease

    def _on_new_frame(self, timeline, timing):
        x, y = self._actor.get_position()
        self.move(int(x), int(y))

    def animated_move(self, x, y):
        orig_x, orig_y = self.get_position()
        self._actor.set_position(orig_x, orig_y)
        self._actor.set_size(self.allocation.width, self.allocation.height)
        animation = self._actor.animate(
            self.ease, 250, "x", x, "y", y)
        timeline = animation.get_timeline()
        timeline.connect('new-frame', self._on_new_frame)
        
        return animation
        
if __name__ == "__main__":
    import gtk
    class AnimatedWindow(gtk.Window, AnimatedWindowBase):
        def __init__(self):
            gtk.Window.__init__(self)
            AnimatedWindowBase.__init__(self)

    aw = AnimatedWindow()
    aw.show_all()
    aw.move(100, 100)
    aw.animated_move(200, 200)
    gtk.main()


