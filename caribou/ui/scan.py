import gobject
import pyatspi
from gi.repository import Gdk
from gi.repository import Gtk
import caribou.common.const as const
from caribou.common.settings_manager import SettingsManager

# Scan constants
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

class ScanMaster():
    def __init__(self, root_window, keyboard=None):
        self.root_window = root_window
        self._timer = 0
        self._scan_path = None
        self.started = False

        SettingsManager.step_time.connect("value-changed",
                                          self._on_step_time_changed)
        SettingsManager.scanning_type.connect("value-changed",
                                              self._on_scanning_type_changed)
        if keyboard:
            self.set_keyboard(keyboard)

    def start(self):
        if self.started: return

        if self._timer == 0:
            self._timer = gobject.timeout_add(
                int(SettingsManager.step_time.value*1000), self._scan)

        self._grab_mouse_events()

        pyatspi.Registry.registerKeystrokeListener(
            self._on_key_pressed, mask=0, kind=(pyatspi.KEY_PRESSED_EVENT,))

    def stop(self):
        if self.started: return

        self._ungrab_mouse_events()

        if self._last_block is not None:
            self._multi_map(lambda x: x.scan_highlight_clear(), self._last_block)

        if self._timer != 0:
            gobject.source_remove(self._timer)
            self._timer = 0

        pyatspi.Registry.deregisterKeystrokeListener(
            self._on_key_pressed, mask=0, kind=pyatspi.KEY_PRESSED_EVENT)

    def _on_scanning_type_changed(self, setting, val):
        layout = self.keyboard.get_current_layout()
        if SettingsManager.scanning_type.value == ROW:
            self._blocks = layout.get_scan_rows()
        else:
            self._blocks = layout.get_scan_blocks()

    def _on_step_time_changed(self, setting, val):
        if self._timer != 0:
            gobject.source_remove(self._timer)
            self._timer = gobject.timeout_add(int(1000*val), self._scan)

    def _on_layout_activated(self, keyboard, layout, num):
        if SettingsManager.scanning_type.value == ROW:
            self._blocks = layout.get_scan_rows()
        else:
            self._blocks = layout.get_scan_blocks()
        if SettingsManager.reverse_scanning.value:
            self._scan_path = [0]
        else:
            self._scan_path = [-1]

    def set_keyboard(self, keyboard):
        self._last_block = None
        keyboard.connect("switch-page", self._on_layout_activated)
        self.keyboard = keyboard

    def _multi_map(self, func, array):
        if isinstance(array, list):
            for item in array:
                self._multi_map(func, item)
        else:
            func(array)

    def _get_element_at_path(self, array, path):
        element = array
        for index in path:
            element = element[index]
        return element

    def _get_next_reverse_block(self):
        cancel = False

        if self._scan_path[-1] > 0:
            self._scan_path = self._scan_path[:-1] + [0]
            
        self._scan_path += [self._scan_path.pop() - 1]

        try:
            block = self._get_element_at_path(self._blocks,
                                              self._scan_path)
        except IndexError:
            if len(self._scan_path) == 1:
                block = self._blocks[-1]
                self._scan_path = [-1]
            else:
                block = self._get_element_at_path(
                    self._blocks, self._scan_path[:-1])
                self._scan_path = self._scan_path[:-1] + [0]
                cancel = True

        return cancel, block
                

    def _get_next_block(self):
        cancel = False
        self._scan_path += [self._scan_path.pop() + 1]
        try:
            block = self._get_element_at_path(self._blocks,
                                              self._scan_path)
        except IndexError:
            if len(self._scan_path) == 1:
                block = self._blocks[0]
                self._scan_path = [0]
            else:
                block = self._get_element_at_path(
                    self._blocks, self._scan_path[:-1])
                self._scan_path = self._scan_path[:-1] + [-1]
                cancel = True

        return cancel, block

    def _scan(self):
        if self._scan_path is None: return True

        if self._last_block is not None:
            self._multi_map(lambda x: x.scan_highlight_clear(), self._last_block)

        if SettingsManager.reverse_scanning.value:
            self._cancel, next_block = self._get_next_reverse_block()
        else:
            self._cancel, next_block = self._get_next_block()

        if self._cancel:
            self._multi_map(lambda x: x.scan_highlight_cancel(), next_block)
        elif isinstance(next_block, list):
            if SettingsManager.scanning_type.value == ROW:
                self._multi_map(lambda x: x.scan_highlight_row(), next_block)
            else:
                self._multi_map(lambda x: x.scan_highlight_block(), next_block)
        else:            
            self._multi_map(lambda x: x.scan_highlight_key(), next_block)

        self._last_block = next_block
        return True

    def _do_switch(self):
        if self._cancel:
            assert(len(self._scan_path) > 1)
            self._scan_path.pop()
        elif isinstance(self._last_block, list):
            assert(len(self._last_block) > 0)
            if SettingsManager.reverse_scanning.value:
                self._scan_path.append(0)
            else:
                self._scan_path.append(-1)
        else:
            self._last_block.clicked()

    def _grab_mouse_events(self):
        Gdk.event_handler_set(self._mouse_handler, None)

    def _ungrab_mouse_events(self):
        Gdk.event_handler_set(Gtk.main_do_event, None)

    def _mouse_handler(self, event, user_data):
        if SettingsManager.switch_type.value != MOUSE_SWITCH_TYPE or \
                event.type not in (Gdk.EventType.BUTTON_PRESS,
                                   Gdk.EventType.ENTER_NOTIFY):
            Gtk.main_do_event(event)
            return

        if self.root_window.get_window().is_visible():
            if event.type == Gdk.EventType.BUTTON_PRESS and \
                    str(event.button.button) == \
                    SettingsManager.mouse_button.value:
                self._do_switch()
            elif event.type != Gdk.EventType.ENTER_NOTIFY:
                Gtk.main_do_event(event)
        else:
            Gtk.main_do_event(event)

    def _on_key_pressed(self, event):
        if SettingsManager.switch_type.value == KEYBOARD_SWITCH_TYPE and \
                SettingsManager.keyboard_key.value == event.event_string:
            self._do_switch()
