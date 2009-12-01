# -*- coding: utf-8 -*-
#
# Carbou - On-screen Keyboard and UI navigation application
#
# Copyright (C) 2009 Adaptive Technology Resource Centre
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
import gobject
import gtk.gdk as gdk
import pango
import virtkey
import qwerty

class CaribouPredicitionArea(gtk.HBox):
    pass

# TODO validate keyboard by creating this object and catching exception
class CaribouKeyboard(gtk.Frame):

    def __init__(self, keyboard):
        gtk.Frame.__init__(self)
        self.set_shadow_type(gtk.SHADOW_NONE)

        # FIXME use references instead of this??
        self._layouts = []
        self._vk = virtkey.virtkey()

        switch_buttons = []
        for layout in keyboard.layouts:
            layoutvbox = gtk.VBox(homogeneous=True)
            layoutvbox.set_name(layout)
            layout = getattr(keyboard, layout)
            for row in layout:
                rowhbox = gtk.HBox(homogeneous=True)
                for key in row:
                    # check if the key is a simple str or a key defined by a tuple
                    if isinstance(key, str):
                        button = gtk.Button(key)
                        char = ord(key.decode('utf-8'))
                        button.connect("clicked", self.__send_unicode, char)
                    elif isinstance(key, tuple):
                        button = gtk.Button(key[0])
                        # check if this key is a layout switch key or not
                        if isinstance(key[1], str):
                            # switch layout key
                            # set layer name on button and save to process later
                            button.set_name(key[1])
                            switch_buttons.append(button)
                        else:
                            # regular key
                            button.connect("clicked", self.__send_keysym, key[1])
                    else:
                        pass #TODO throw error here

                    rowhbox.pack_start(button, expand=False, fill=True)

                layoutvbox.pack_start(rowhbox, expand=False, fill=False)

            self._layouts.append(layoutvbox)

        for button in switch_buttons:
            for layout in self._layouts:
                if button.get_name() == layout.get_name():
                    button.connect("clicked", self.__change_layout, layout)
                    button.set_name("")
                    break
            else:
                print "ERROR" # TODO throw exception

        # add the first layer and make it visible
        self.add(self._layouts[0])
        self.show_all()

    def __send_unicode(self, widget, data):
        self._vk.press_unicode(data)
        self._vk.release_unicode(data)

    def __send_keysym(self, widget, data):
        self._vk.press_keysym(data)
        self._vk.release_keysym(data)

    def __change_layout(self, widget, data):
        self.remove(self.get_child())
        self.add(data)
        self.show_all()

gobject.type_register(CaribouKeyboard)

class CaribouWindow(gtk.Window):
    __gtype_name__ = "CaribouWindow"

    def __init__(self):
        super(CaribouWindow, self).__init__(gtk.WINDOW_POPUP)
        self.set_name("CaribouWindow")

        self._vbox = gtk.VBox()
        self.add(self._vbox)

        self._vbox.pack_start(CaribouKeyboard(qwerty))

class CaribouHoverWindow(CaribouWindow):
    __gtype_name__ = "CaribouHoverWindow"

    def __init__(self, default_placement=None):
        super(CaribouHoverWindow, self).__init__()

        self.connect("size-allocate", lambda w, a: self._update_position())

        self._cursor_location = gtk.gdk.Rectangle()
        self._entry_location = gtk.gdk.Rectangle()
        self._default_placement = default_placement or \
            CaribouKeyboardPlacement()
    

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
            
    def _update_position(self, placement=None):
        placement = placement or self._default_placement

        x = self._calculate_axis(placement.x)
        y = self._calculate_axis(placement.y)

        self.move(x, y)

    def _calculate_axis(self, axis_placement):
        root_bbox = self._get_root_bbox()
        bbox = root_bbox

        if axis_placement.stickto == CaribouKeyboardPlacement.CURSOR:
            bbox = self._cursor_location
        elif axis_placement.stickto == CaribouKeyboardPlacement.ENTRY:
            bbox = self._entry_location

        offset = axis_placement.get_offset(bbox)

        if axis_placement.align == CaribouKeyboardPlacement.END:
            offset += axis_placement.get_length(bbox)
        elif axis_placement.halign == CaribouKeyboardPlacement.CENTER:
            offset += axis_placement.get_length(bbox)/2

        return offset

class CaribouKeyboardPlacement(object):
    START = 'start'
    END = 'end'
    CENTER = 'center'
    
    SCREEN = 'screen'
    ENTRY = 'entry'
    CURSOR = 'cursor'
    
    INSIDE = 'inside'
    OUTSIDE = 'outside'
    
    class _AxisPlacement(object):
        def __init__(self, axis, align=None, stickto=None, gravitate=None):
            self.axis = axis
            self.align = align or CaribouKeyboardPlacement.END
            self.stickto = stickto or CaribouKeyboardPlacement.CURSOR
            self.gravitate = gravitate or CaribouKeyboardPlacement.OUTSIDE

        def copy(self, align=None, stickto=None, gravitate=None):
            return self.__class__(self.axis,
                                  align or self.align, 
                                  stickto or self.stickto, 
                                  gravitate or self.gravitate)

        def get_offset(self, bbox):
            return bbox.x if self.axis == 'x' else bbox.y
        
        def get_length(self, bbox):
            return bbox.width if self.axis == 'x' else bbox.height

    def __init__(self, x=None, y=None):
        self.x = x or self._AxisPlacement('x')
        self.y = y or self._AxisPlacement('y')

if __name__ == "__main__":
    ckbd = CaribouHoverWindow()
    ckbd.show_all()
    gtk.main()

