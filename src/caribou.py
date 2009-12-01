#
# Carbou - text entry and UI navigation application
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

import pyatspi
import gtk
import keyboard
import gettext
import getopt
import sys

_ = gettext.gettext

debug = False

class Test:
    def __init__(self):
        self.__current_acc = None 

    def on_text_caret_moved(self, event):
        if self.__current_acc == event.source:
            self.__set_location(event.source)
            if debug == True:
                print "object:text-caret-moved in", event.host_application.name, event.detail1, event.source.description
    
    def __set_text_location(self, acc):
        text = acc.queryText() 
        [x, y, width, height] = text.getCharacterExtents(text.caretOffset, pyatspi.DESKTOP_COORDS)
        cp.set_cursor_location(x, y + height)
        cp.show_all()
       
    def __set_entry_location(self, acc):
        text = acc.queryText()
        [x, y, width, height] = text.getCharacterExtents(text.caretOffset, pyatspi.DESKTOP_COORDS)
        if x == 0 and y == 0 and width == 0 and height == 0:
            component = acc.queryComponent()
            bb = component.getExtents(pyatspi.DESKTOP_COORDS)
            cp.set_cursor_location(bb.x, bb.y + bb.height)
        else:
            cp.set_cursor_location(x, y + height)
        cp.show_all()
       
    def on_state_changed_focused(self, event):
        acc = event.source
        if pyatspi.STATE_EDITABLE in acc.getState().getStates():
            if event.source_role == pyatspi.ROLE_TEXT:
                if event.detail1 == 1:
                    self.__set_text_location(acc)
                    self.__current_acc = event.source
                    self.__set_location = self.__set_text_location
                    if debug == True:
                        print "enter text widget in", event.host_application.name
                elif event.detail1 == 0:
                    cp.hide_all()
                    self.__current_acc = None 
                    self.__set_location = None
                    if debug == True:
                        print "leave text widget in", event.host_application.name

            elif event.source_role == pyatspi.ROLE_ENTRY:
                if event.detail1 == 1:
                    self.__set_entry_location(acc)
                    self.__current_acc = event.source
                    self.__set_location = self.__set_entry_location
                    if debug == True:
                        print "enter entry widget in", event.host_application.name
                elif event.detail1 == 0:
                    cp.hide_all()
                    self.__current_acc = None 
                    self.__set_location = None
                    if debug == True:
                        print "leave entry widget in", event.host_application.name
            else:
                print _("WARNING - Caribou: unhandled editable widget:"), event.source         

        # Firefox does report leave entry widget events.
        # This could be a way to get the entry widget leave events.
        #else:
        #    if event.detail1 == 1:
        #        cp.hide_all()
        #        print "--> LEAVE EDITABLE TEXT <--"

    def on_key_down(self, event):
        # key binding for controling the row column scanning
        # TODO: needs implementing
        if event.event_string == "Shift_R":
            pass 
        elif event.event_string == "Control_R":
            if debug == True:
                print "quitting ..."
            # TODO: use for loop here? see below
            result = pyatspi.Registry.deregisterEventListener(self.on_text_caret_moved, "object:text-caret-moved")
            if debug == True:
                print "deregisterEventListener - object:text-caret-moved ...",
                if result == False:
                    print "OK"
                else:
                    print "FAIL"
            result = pyatspi.Registry.deregisterEventListener(self.on_state_changed_focused, "object:state-changed:focused")
            if debug == True:
                print "deregisterEventListener - object:state-changed:focused ...",
                if result == False:
                    print "OK"
                else:
                    print "FAIL"
            result = pyatspi.Registry.deregisterKeystrokeListener(self.on_key_down, mask = None, kind = (pyatspi.KEY_PRESSED_EVENT,))
            if debug == True:
                print "deregisterKeystrokeListener"
            gtk.main_quit()


def usage():
    """Prints out usage information."""
    print _("Usage:")
    print "  " + sys.argv[0] + _(" [OPTION...]")
    print
    print _("Help Options:")
    print "  -d, --debug                      " + _("Print debug messages on stdout")
    print "  -h, --help                       " + _("Show this help message")

if __name__ == "__main__":

    try:
        options, xargs = getopt.getopt(sys.argv[1:], "dh", ["debug", "help"])
    except getopt.GetoptError, e:
        print "Error: " + e.__str__() + "\n"
        usage()
        sys.exit(1)
 
    for opt, val in options:
        if opt in ("-d", "--debug"):
            debug = True

        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)

    test = Test()
    # TODO: make a for loop
    #EVENTS = ["object:state-changed:focused", "object:text-caret-moved"]
    #for f in dir(test):
    #    print f, isinstance(f, str)
    pyatspi.Registry.registerEventListener(test.on_state_changed_focused, "object:state-changed:focused")
    pyatspi.Registry.registerEventListener(test.on_text_caret_moved, "object:text-caret-moved")
    pyatspi.Registry.registerKeystrokeListener(test.on_key_down, mask = None, kind = (pyatspi.KEY_PRESSED_EVENT,))

    # TODO: move text entry detection to its own file
    cp = keyboard.CaribouWindow()
    cp.hide_all()
 
    gtk.main()
