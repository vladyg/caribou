import gobject
import pyatspi
from gi.repository import Gdk
from gi.repository import Gtk
import caribou.common.const as const
from caribou.common.settings_manager import SettingsManager

# Scan constans
BUTTON = 'button'
ROW = 'row'
BLOCK = 'block'
CANCEL = 'cancel'
REVERSE = 'reverse'
MOUSE_SWITCH_TYPE = 'mouse'
KEYBOARD_SWITCH_TYPE = 'keyboard'
KEYBOARD_KEY_LIST = {"Shift R" : "Shift_R",
                     "Shift L" : "Shift_L", 
                     "Alt Gr"  : "ISO_Level3_Shift",
                     "Num Lock": "Num_Lock"}
DEFAULT_KEYBOARD_KEY = 'Shift R'
DEFAULT_MOUSE_BUTTON = '1'
MIN_STEP_TIME = 50
MAX_STEP_TIME = 5000
TIME_SINGLE_INCREMENT = 1
TIME_MULTI_INCREMENT = 10
DEFAULT_STEP_TIME = 1000
DEFAULT_SCANNING_TYPE = ROW
DEFAULT_SWITCH_TYPE = KEYBOARD_SWITCH_TYPE

class ScanService():
    def __init__(self, keyboard, root_window):
        self.keyboard = keyboard
        self.root_window = root_window
        self.selected_row = None
        self.selected_button = None
        self.button_index = 0
        self.row_index = 0
        self.index_i = 0
        self.index_j = 0
        self.is_stop = True
        self.timerid = None
        self.reverse = False
        self.selected_block = []

        # Settings we are interested in.
        for name in ["step_time", "reverse_scanning", "scanning_type"]:
            getattr(SettingsManager, name).connect("value-changed",
                                                   self._on_switch_changed)

        for name in ["switch_type", "mouse_button", "keyboard_key"]:
            getattr(SettingsManager, name).connect("value-changed",
                                                   self._on_switch_changed)
        
        for name in ["default_colors", "normal_color", "mouse_over_color",
                     "row_scanning_color", "button_scanning_color",
                     "cancel_scanning_color", "block_scanning_color"]:
            getattr(SettingsManager, name).connect("value-changed",
                                                   self._on_color_changed)

        SettingsManager.scan_enabled.connect("value-changed",
                                             self._on_scan_toggled)

        self._configure_scanning()
        self._set_colors()
        self._configure_switch()

    def destroy(self):
        self.stop()
        self.clean()
        self._deregister_events()


    def _configure_switch(self):
        self.switch_type = SettingsManager.switch_type.value
        if self.switch_type == MOUSE_SWITCH_TYPE:
            self.switch_key = SettingsManager.mouse_button.value
        elif self.switch_type == KEYBOARD_SWITCH_TYPE:
            self.switch_key = SettingsManager.keyboard_key

        try:
            pyatspi.Registry.registerKeystrokeListener(self._on_key_pressed, 
                                mask=None, kind=(pyatspi.KEY_PRESSED_EVENT,))
            pyatspi.Registry.registerKeystrokeListener(self._on_key_released, 
                                mask=None, kind=(pyatspi.KEY_RELEASED_EVENT,))
        except:
            print "Error while registering keyboard events in scan.py"

    def _deregister_events(self):
        try:
            pyatspi.Registry.deregisterKeystrokeListener(self._on_key_pressed, 
                                mask=None, kind=pyatspi.KEY_PRESSED_EVENT)
            pyatspi.Registry.deregisterKeystrokeListener(
                                self._on_key_released, 
                                mask=None, kind=pyatspi.KEY_RELEASED_EVENT)
        except:
            print "Error while deregistering keyboard events in scan.py"

    def _on_switch_changed(self, settings, val):
        self._deregister_events()
        self._configure_switch()

    def _on_scan_toggled(self, settings, val):
        if val:
            self.start()
        else:
            self.stop()

    def _on_color_changed(self, settings, val):
        self._set_colors()

    def _on_scanning_type_changed(self, settings, val):
        self._configure_scanning()

    def _configure_scanning(self):
        if not self.is_stop:
            self._stop()
        self.scanning_type = SettingsManager.scanning_type.value
        self.reverse = SettingsManager.reverse_scanning.value
        self.step_time = SettingsManager.step_time.value

        if self.scanning_type == BLOCK:
            self.selected_block = []
        else:
            self.selected_block = self.keyboard
        self.scanning = self.scanning_type

    def _set_colors(self):
        self.default_colors = SettingsManager.default_colors.value
        self.normal_color = SettingsManager.normal_color.value
        self.mouse_over_color = SettingsManager.mouse_over_color.value
        self.row_scanning_color = SettingsManager.row_scanning_color.value
        self.button_scanning_color = \
            SettingsManager.button_scanning_color.value
        self.cancel_scanning_color = \
            SettingsManager.cancel_scanning_color.value
        self.block_scanning_color = SettingsManager.block_scanning_color.value

    # public start
    def start(self, scanning=None):
        self.scanning = scanning or self.scanning_type
        self.clean()
        if self.root_window and \
            self.switch_type == MOUSE_SWITCH_TYPE:
            self._grab_mouse_events()

        if not self.reverse:
            self.reset(self.scanning)

    # public stop
    def stop(self):
        if self.switch_type == MOUSE_SWITCH_TYPE:
            self._ungrab_mouse_events()
        self.clean()
        self._stop()

    #private start
    def _start(self, scanning=ROW):
        if self.is_stop == True and self.timerid == None:
            self.is_stop = False
            self.button_index = -1
            self.row_index = -1
            if scanning == ROW:
                self.selected_row = []
                self.timerid = gobject.timeout_add(
                    int(1000*self.step_time), self._scan_row)
            elif scanning == BUTTON:
                self.selected_button = None
                self.timerid = gobject.timeout_add(
                    int(1000*self.step_time), self._scan_button)
            elif scanning == BLOCK:
                self.selected_block = []
                self.selected_row = []
                self.clean()
                self.index_i = 2
                self.index_j = 1
                self.timerid = gobject.timeout_add(
                    int(1000*self.step_time), self._scan_block)

    # private stop
    def _stop(self):
        self.is_stop = True
        if self.timerid:
            gobject.source_remove(self.timerid)
            self.timerid = None

    def reset(self, scanning=ROW):
        self._stop()
        self._start(scanning)

    def clean(self):
        for row in self.keyboard:
            for button in row:
                self.select_button(button, False)


    def change_keyboard(self, keyboard):
        if not self.is_stop:
            self._stop()
        self.keyboard = keyboard
        self.scanning = self.scanning_type
        self.start(self.scanning_type)
        if self.scanning == ROW:
            self.selected_block = keyboard


    def _grab_mouse_events(self):
        Gdk.event_handler_set(self._mouse_handler)

    def _ungrab_mouse_events(self):
        Gdk.event_handler_set(Gtk.main_do_event)

    def _mouse_handler(self, event):
        if self.root_window.window.is_visible():
            if event.type == Gdk.EventType.BUTTON_PRESS and \
                str(event.button) == self.switch_key.value:
                self._handle_press()
            elif event.type == Gdk.BUTTON_RELEASE and \
                str(event.button) == self.switch_key.value:
                self._handle_release()
            elif not event.type == Gdk.ENTER_NOTIFY:
                Gtk.main_do_event(event)
        else:
            Gtk.main_do_event(event)

    def _scan_block(self):
        if self.is_stop:
            return False
        # Clean the previous block
        self.select_block(self.selected_block, False)
        # Update indexes, three horizontal blocks, and two vertical
        if self.index_j < 2:
            self.index_j += 1
        elif self.index_i < 1:
            self.index_i += 1
            self.index_j = 0
        else:
            self.index_j = 0
            self.index_i = 0

        self.selected_block = []
        #width = self.root_window.size_request()[0]
        #height = self.root_window.size_request()[1]
        root_x = self.root_window.get_position()[0]
        root_y = self.root_window.get_position()[1]
        offset_w = self.index_j*(width/3)
        offset_h = self.index_i*(height/2)

        block_window = (root_x + offset_w, 
                                         root_y + offset_h, 
                                         width/3, 
                                         height/2)
        empty_r = ()
        try:
            for row in self.keyboard:
                line = []
                for button in row:
                    abs_b_x = button.get_allocation()[0] + \
                              button.window.get_position()[0]
                    abs_b_y = button.get_allocation()[1] + \
                              button.window.get_position()[1]
                    abs_b_r = (abs_b_x, 
                                               abs_b_y,
                                               button.size_request()[0],
                                               button.size_request()[1])

            # If button rectangle is inside the block:
                    intersect = block_window.intersect(abs_b_r)
                # If the intersected rectangle != empty
                    if intersect != empty_r:
                        # If the witdth of intersection is bigger than half 
                        # of button width and height, we append button to line
                        if (intersect.width > (abs_b_r.width / 2)) and \
                           (intersect.height > (abs_b_r.height / 2)):
                           line.append(button)


                if len(line) > 0:
                    self.selected_block.append(line)
                    
        except Exception as e:
            self.is_stop = True
            return False
            
        self.select_block(self.selected_block, True,
                           self.block_scanning_color)
        return True       
                                               


    def _scan_row(self):
        if self.is_stop:
            return False

        else:
            self.select_row(self.selected_row, 
                            self.scanning_type == BLOCK, 
                            self.block_scanning_color)
            self.row_index += 1
            if self.row_index >= len(self.selected_block):
                self.row_index = 0
            self.selected_row = self.selected_block[self.row_index]
            self.select_row(self.selected_row, True, self.row_scanning_color)
            return True

    def _scan_button(self):
        if self.scanning == CANCEL:
            self.scanning = BUTTON
            self.selected_button = None
            self.select_row(self.selected_row, True, self.row_scanning_color)
            return True
        else:
            if self.selected_button and self.selected_button in self.selected_row:
                self.select_button(self.selected_button, True, self.row_scanning_color)

            if self.is_stop:
                return False

            self.button_index += 1
            if self.button_index >= len(self.selected_row):
                self.select_row(self.selected_row, True, self.cancel_scanning_color)
                self.button_index = -1
                self.scanning = CANCEL
                return True

            self.selected_button = self.selected_row[self.button_index]
            while self.selected_button.key_type == const.DUMMY_KEY_TYPE:
                self.button_index += 1
                if self.button_index >= len(self.selected_row):
                    self.select_row(self.selected_row, True, self.cancel_scanning_color)
                    self.button_index = -1
                    self.scanning = CANCEL
                    return True

                self.selected_button = self.selected_row[self.button_index]
            self.select_button(self.selected_button, True, self.button_scanning_color)
            return True

    def select_block(self, block, state, color=None):
        for row in block:
            self.select_row(row, state, color)

    def select_row(self, row, state, color=None):
        for button in row:
            self.select_button(button, state, color)

    def select_button(self, button, state, color=None):
        if state:
            button.set_color(color, self.mouse_over_color)
        elif self.default_colors:
            button.reset_color()
        else:
            button.set_color(self.normal_color,
                             self.mouse_over_color)

    def _on_key_pressed(self, event):
        if event.event_string == "Escape":
            SettingsManager.scan_enabled.value = False
        elif self.switch_type == KEYBOARD_SWITCH_TYPE and \
             self.switch_key.value == event.event_string:
            self._handle_press()

    def _on_key_released(self, event):
        if self.switch_type == KEYBOARD_SWITCH_TYPE and \
                self.switch_key.value == event.event_string:
            self._handle_release()
        elif event.event_string != "Escape": 
            self._stop()
            self.start()

    def _handle_press(self):
        if self.reverse:
            self._start(self.scanning)

    def _handle_release(self):
        if self.reverse:
            if not self.is_stop:
                if self.scanning == ROW and \
                        len(self.selected_row) > 0:
                    self.scanning = BUTTON
                elif self.scanning == BLOCK and \
                        len(self.selected_block) > 0:
                    self.scanning = ROW
                elif self.scanning == BUTTON and \
                        self.selected_button:
                    self.clean()
                    if self.selected_button.key_type == const.PREFERENCES_KEY_TYPE:
                        self.stop()
                    self.selected_button.clicked()
                    self.selected_button = None
                    self.scanning = self.scanning_type
                    self.reset()

                elif self.scanning == CANCEL:
                    self.clean()
                    self.scanning = self.scanning_type
                self._stop()

        else:
            if not self.is_stop:
                if self.scanning == ROW and \
                        len(self.selected_row) > 0:
                    self.scanning = BUTTON
                    self.reset(BUTTON)

                elif self.scanning == BLOCK and \
                        len(self.selected_block) > 0:
                    self.scanning = ROW
                    self.reset(ROW)
                elif self.scanning == BUTTON and \
                        self.selected_button:
                    self.selected_button.clicked()
                    self.scanning = ROW
                    if self.selected_button.key_type \
                            == const.PREFERENCES_KEY_TYPE:
                        self.selected_button = None
                        self.stop()
                    else: 
                        self.selected_button = None
                        self.scanning = self.scanning_type

                elif self.scanning == CANCEL:
                    self.scanning = self.scanning_type
                    self.clean()
                    self.reset(self.scanning_type)

               
