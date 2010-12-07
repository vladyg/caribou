import gobject
import pyatspi
import gtk
import caribou.common.const as const
import gconf

class Scan_service():
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
        self.client = gconf.client_get_default()
        self._gconf_connections = []
        self._gconf_connections.append(self.client.notify_add(
                            const.CARIBOU_GCONF + "/scanning_type", 
                            self._on_scanning_type_changed))
        self._gconf_connections.append(self.client.notify_add(
                            const.CARIBOU_GCONF + "/step_time", 
                            self._on_scanning_type_changed))
        self._gconf_connections.append(self.client.notify_add(
                            const.CARIBOU_GCONF + "/reverse_scanning", 
                            self._on_scanning_type_changed))
        self._gconf_connections.append(self.client.notify_add(
                            const.CARIBOU_GCONF + "/switch_type",
                            self._on_switch_changed))
        self._gconf_connections.append(self.client.notify_add(
                            const.CARIBOU_GCONF + "/mouse_button",
                            self._on_switch_changed))
        self._gconf_connections.append(self.client.notify_add(
                            const.CARIBOU_GCONF + "/keyboard_key", 
                            self._on_switch_changed))

        self._gconf_connections.append(self.client.notify_add(
                            const.CARIBOU_GCONF + "/default_colors",
                            self._on_color_changed))
        self._gconf_connections.append(self.client.notify_add(
                            const.CARIBOU_GCONF + "/normal_color", 
                            self._on_color_changed))
        self._gconf_connections.append(self.client.notify_add(
                            const.CARIBOU_GCONF + "/mouse_over_color", 
                            self._on_color_changed))
        self._gconf_connections.append(self.client.notify_add(
                            const.CARIBOU_GCONF + "/row_scanning_color", 
                            self._on_color_changed))
        self._gconf_connections.append(self.client.notify_add(
                            const.CARIBOU_GCONF + "/button_scanning_color", 
                            self._on_color_changed))
        self._gconf_connections.append(self.client.notify_add(
                            const.CARIBOU_GCONF + "/cancel_scanning_color", 
                            self._on_color_changed))
        self._gconf_connections.append(self.client.notify_add(
                            const.CARIBOU_GCONF + "/block_scanning_color", 
                            self._on_color_changed))
        self._configure_scanning()
        self._set_colors()
        self._configure_switch()

    def destroy(self):
        self.stop()
        self.clean()
        self._deregister_events()
        for id in self._gconf_connections:
            self.client.notify_remove(id)



    def _configure_switch(self):
        self.switch_type = self.client.get_string(const.CARIBOU_GCONF + 
                                                  "/switch_type") or "mouse"
        if self.switch_type == const.MOUSE_SWITCH_TYPE:
            self.switch_key = self.client.get_string(const.CARIBOU_GCONF + 
                                                     "/mouse_button") or "2"
        elif self.switch_type == const.KEYBOARD_SWITCH_TYPE:
            self.switch_key = self.client.get_string(const.CARIBOU_GCONF +
                                                     "/keyboard_key") or "Shift_L"
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
                                mask=None, kind=(pyatspi.KEY_PRESSED_EVENT,))
            pyatspi.Registry.deregisterKeystrokeListener(
                                self._on_key_released, 
                                mask=None, kind=(pyatspi.KEY_RELEASED_EVENT,))
        except:
            print "Error while deregistering keyboard events in scan.py"

    def _on_switch_changed(self, client, connection_id, entry, args):
        self._deregister_events()
        self._configure_switch()

    def _on_color_changed(self, client, connection_id, entry, args):
        self._set_colors()

    def _on_scanning_type_changed(self, client, connection_id, entry, args):
        self._configure_scanning()

    def _configure_scanning(self):
        if not self.is_stop:
            self._stop()
        self.scanning_type = self.client.get_string(const.CARIBOU_GCONF +
                                                    "/scanning_type") or "0"
        self.reverse = self.client.get_bool(const.CARIBOU_GCONF +
                                                    "/reverse_scanning") or False
        self.step_time = self.client.get_int(const.CARIBOU_GCONF + 
                                                    "/step_time") or 1000
        if self.scanning_type == const.BLOCK:
            self.selected_block = []
        else:
            self.selected_block = self.keyboard
        self.scanning = self.scanning_type

    def _set_colors(self):
        self.default_colors = self.client.get_bool(
                                const.CARIBOU_GCONF + "/default_colors") \
                                or True
        self.normal_color = self.client.get_string(
                                const.CARIBOU_GCONF + "/normal_color") \
                                or "gray80"
        self.mouse_over_color = self.client.get_string(
                                const.CARIBOU_GCONF + "/mouse_over_color") \
                                or "yellow"

        self.row_scanning_color = self.client.get_string(
                                const.CARIBOU_GCONF + "/row_scanning_color") \
                                or "green"
        self.button_scanning_color = self.client.get_string(
                            const.CARIBOU_GCONF + "/button_scanning_color") \
                            or "cyan"
        self.cancel_scanning_color = self.client.get_string(
                            const.CARIBOU_GCONF + "/cancel_scanning_color") \
                            or "red"
        self.block_scanning_color = self.client.get_string(
                            const.CARIBOU_GCONF + "/block_scanning_color") \
                            or "purple" 


    # public start
    def start(self, scanning=None):
        self.scanning = scanning or self.scanning_type
        self.clean()
        if self.root_window and \
            self.switch_type == const.MOUSE_SWITCH_TYPE:
            self._grab_mouse_events()

        if not self.reverse:
            self.reset(self.scanning)

    # public stop
    def stop(self):
        if self.switch_type == const.MOUSE_SWITCH_TYPE:
            self._ungrab_mouse_events()
        self.clean()
        self._stop()

    #private start
    def _start(self, scanning=const.ROW):
        if self.is_stop == True and self.timerid == None:
            self.is_stop = False
            self.button_index = -1
            self.row_index = -1
            if scanning == const.ROW:
                self.selected_row = []
                self.timerid = gobject.timeout_add(self.step_time, self._scan_row)
            elif scanning == const.BUTTON:
                self.selected_button = None
                self.timerid = gobject.timeout_add(self.step_time, self._scan_button)
            elif scanning == const.BLOCK:
                self.selected_block = []
                self.selected_row = []
                self.clean()
                self.index_i = 2
                self.index_j = 1
                self.timerid = gobject.timeout_add(self.step_time, self._scan_block)

    # private stop
    def _stop(self):
        self.is_stop = True
        if self.timerid:
            gobject.source_remove(self.timerid)
            self.timerid = None

    def reset(self, scanning=const.ROW):
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
        if self.scanning == const.ROW:
            self.selected_block = keyboard


    def _grab_mouse_events(self):
        gtk.gdk.event_handler_set(self._mouse_handler)

    def _ungrab_mouse_events(self):
        gtk.gdk.event_handler_set(gtk.main_do_event)

    def _mouse_handler(self, event):
        if self.root_window.window.is_visible():
            if event.type == gtk.gdk.BUTTON_PRESS and \
                str(event.button) == self.switch_key:
                self._handle_press()
            elif event.type == gtk.gdk.BUTTON_RELEASE and \
                str(event.button) == self.switch_key:
                self._handle_release()
            elif not event.type == gtk.gdk.ENTER_NOTIFY:
                gtk.main_do_event(event)
        else:
            gtk.main_do_event(event)

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
        width = self.root_window.size_request()[0]
        height = self.root_window.size_request()[1]
        root_x = self.root_window.get_position()[0]
        root_y = self.root_window.get_position()[1]
        offset_w = self.index_j*(width/3)
        offset_h = self.index_i*(height/2)

        block_window = gtk.gdk.Rectangle(root_x + offset_w, 
                                         root_y + offset_h, 
                                         width/3, 
                                         height/2)
        empty_r = gtk.gdk.Rectangle()
        try:
            for row in self.keyboard:
                line = []
                for button in row:
                    abs_b_x = button.get_allocation()[0] + \
                              button.window.get_position()[0]
                    abs_b_y = button.get_allocation()[1] + \
                              button.window.get_position()[1]
                    abs_b_r = gtk.gdk.Rectangle(abs_b_x, 
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
                            self.scanning_type == const.BLOCK, 
                            self.block_scanning_color)
            self.row_index += 1
            if self.row_index >= len(self.selected_block):
                self.row_index = 0
            self.selected_row = self.selected_block[self.row_index]
            self.select_row(self.selected_row, True, self.row_scanning_color)
            return True

    def _scan_button(self):
        if self.scanning == const.CANCEL:
            self.scanning = const.BUTTON
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
                self.scanning = const.CANCEL
                return True

            self.selected_button = self.selected_row[self.button_index]
            while self.selected_button.key_type == const.DUMMY_KEY_TYPE:
                self.button_index += 1
                if self.button_index >= len(self.selected_row):
                    self.select_row(self.selected_row, True, self.cancel_scanning_color)
                    self.button_index = -1
                    self.scanning = const.CANCEL
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
            button.set_color(self.normal_color, self.mouse_over_color)


    def _on_key_pressed(self, event):
        if event.event_string == "Escape":
            self.stop()
        elif self.switch_type == const.KEYBOARD_SWITCH_TYPE and \
             self.switch_key == event.event_string:
            self._handle_press()

    def _on_key_released(self, event):
            if self.switch_type == const.KEYBOARD_SWITCH_TYPE and \
                 self.switch_key == event.event_string:
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
                if self.scanning == const.ROW and \
                        len(self.selected_row) > 0:
                    self.scanning = const.BUTTON
                elif self.scanning == const.BLOCK and \
                        len(self.selected_block) > 0:
                    self.scanning = const.ROW
                elif self.scanning == const.BUTTON and \
                        self.selected_button:
                    self.clean()
                    if self.selected_button.key_type == const.PREFERENCES_KEY_TYPE:
                        self.stop()
                    self.selected_button.clicked()
                    self.selected_button = None
                    self.scanning = self.scanning_type
                    self.reset()

                elif self.scanning == const.CANCEL:
                    self.clean()
                    self.scanning = self.scanning_type
                self._stop()

        else:
            if not self.is_stop:
                if self.scanning == const.ROW and \
                        len(self.selected_row) > 0:
                    self.scanning = const.BUTTON
                    self.reset(const.BUTTON)

                elif self.scanning == const.BLOCK and \
                        len(self.selected_block) > 0:
                    self.scanning = const.ROW
                    self.reset(const.ROW)
                elif self.scanning == const.BUTTON and \
                        self.selected_button:
                    self.selected_button.clicked()
                    self.scanning = const.ROW
                    if self.selected_button.key_type \
                            == const.PREFERENCES_KEY_TYPE:
                        self.selected_button = None
                        self.stop()
                    else: 
                        self.selected_button = None
                        self.scanning = self.scanning_type

                elif self.scanning == const.CANCEL:
                    self.scanning = self.scanning_type
                    self.clean()
                    self.reset(self.scanning_type)

               
