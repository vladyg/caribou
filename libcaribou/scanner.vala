namespace Caribou {
    /**
     * Object providing access to keyboard in scanning mode.
     */
    public class Scanner : Object {
        public bool bind_settings { get; construct; default=true; }

        private ScanGrouping _scan_grouping;
        public int scan_grouping {
            get {
                return (int) _scan_grouping;
            }

            set construct {
                _scan_grouping = (ScanGrouping) value;
                if (root_group != null)
                    root_group.scan_grouping = _scan_grouping;
                reset ();
            }
        }

        private bool _scan_enabled;
        public bool scan_enabled {
            get { return _scan_enabled; }
            set construct {
                _scan_enabled = value;
                if (_scan_enabled)
                    enable ();
                else
                    disable ();
            }
        }
        
        private double _step_time;
        public double step_time {
            get { return _step_time; }
            set construct {
                _step_time = value;
                if (scan_tid != 0) {
                    GLib.Source.remove (scan_tid);
                    scan_tid = GLib.Timeout.add ((int) (_step_time*1000), scan);
                }
            }
        }

        private string _switch_device;
        public string switch_device {
            get { return _switch_device; }
            set construct {
                _switch_device = value;
                configure_switch ();
            }
        }

        private string _keyboard_key;
        public string keyboard_key {
            get { return _keyboard_key; }
            set construct {
                _keyboard_key = value;
                configure_switch ();
            }
        }

        private int _mouse_button;
        public int mouse_button {
            get { return _mouse_button; }
            set construct {
                _mouse_button = value;
                configure_switch ();
            }
        }

        public int scan_cycles { get; set construct; default=1; }
        public bool autorestart { get; set construct; default=false; }
        public bool inverse_scanning { get; set construct; default=false; }

        private delegate void UnconfigureSwitchFunc();
        private UnconfigureSwitchFunc unconfigure_switch_func;

        private uint scan_tid;
        private KeyboardModel keyboard;
        private IScannableGroup root_group;
        private bool started;

        construct {
            /* defaults */
            _scan_grouping = ScanGrouping.SUBGROUPS;
            _step_time = 1.0;
            _switch_device = "keyboard";

            if (bind_settings)
                do_bind_settings ();
        }

        private void do_bind_settings () {
            Settings caribou_settings = new Settings ("org.gnome.caribou");
            string[] settings = {"scan-grouping", "step-time", "scan-cycles",
                                 "autorestart", "inverse-scanning", "switch-device",
                                 "keyboard-key", "mouse-button", "scan-enabled"};

            foreach (string setting in settings) {
                caribou_settings.bind (setting, this, setting, SettingsBindFlags.GET);
            }
        }

        private bool select () {
            IScannableItem? item = root_group.child_select ();

            if (item is IScannableGroup) {
                step ();
                return true;
            } else {
                reset ();
                return false;
            }
        }

        private void switch_pressed (uint code, bool pressed) {
            if (pressed) {
                if (!started) {
                    step ();
                    start ();
                    return;
                }

                stop ();

                if (inverse_scanning) {
                    step ();
                    start ();
                } else {
                    if (select () || autorestart)
                        start ();
                }
            }
        }

        public void set_keyboard (KeyboardModel keyboard) {
            GroupModel group = keyboard.get_group(keyboard.active_group);
            this.keyboard = keyboard;
            this.keyboard.notify["active-group"].connect(on_group_changed);
            set_active_level (group.get_level (group.active_level));

            foreach (string group_name in keyboard.get_groups()) {
                group = keyboard.get_group(group_name);
                group.notify["active-level"].connect(on_level_changed);
            }
        }

        private void on_level_changed (Object obj, ParamSpec prop) {
            GroupModel group = (GroupModel) obj;
            set_active_level (group.get_level (group.active_level));
        }

        private void on_group_changed (Object obj, ParamSpec prop) {
            GroupModel group = keyboard.get_group(keyboard.active_group);
            set_active_level (group.get_level (group.active_level));
        }

        private void set_active_level (LevelModel level) {
            root_group = (IScannableGroup) level;
            root_group.scan_grouping = _scan_grouping;
        }

        public void reset () {
            if (root_group != null)
                root_group.scan_reset ();
        }

        private void enable () {
            configure_switch ();
        }

        private void disable () {
            unconfigure_switch ();
        }

        private void start () {
            if (started || root_group == null)
                return;

            started = true;

            scan_tid = GLib.Timeout.add((int) (_step_time*1000), scan);
        }

        private void stop () {
            if (!started)
                return;

            started = false;
            if (scan_tid != 0)
                GLib.Source.remove (scan_tid);
            scan_tid = 0;
        }

        private IScannableItem? step () {
            IScannableItem item = root_group.child_step (scan_cycles);            

            if (item == null) {
                reset ();
            }

            return item;
        }

        private bool scan () {
            if (inverse_scanning)
                select ();
            else
                return (step () != null);

            return true;
        }

        private void unconfigure_switch () {
            if (unconfigure_switch_func != null)
                unconfigure_switch_func ();
            unconfigure_switch_func = null;
        }

        private void configure_switch () {
            if (!scan_enabled)
                return;
            
            unconfigure_switch ();

            XAdapter xadapter = XAdapter.get_default();
            if (switch_device == "keyboard" && keyboard_key != null) {
                uint keyval = Gdk.keyval_from_name (keyboard_key);
                xadapter.register_key_func (keyval, switch_pressed);
                unconfigure_switch_func = () => {
                    xadapter.register_key_func (keyval, null);
                };
            } else if (switch_device == "mouse" && mouse_button != 0) {
                xadapter.register_button_func (mouse_button, switch_pressed);
                unconfigure_switch_func = () => {
                    xadapter.register_key_func (mouse_button, null);
                };
            }
        }
    }
}