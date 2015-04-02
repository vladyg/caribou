namespace Caribou {
    public delegate void KeyButtonCallback (uint keybuttoncode, bool pressed);

    /**
     * Base class of singleton object providing access to the display server.
     */
    public abstract class DisplayAdapter : Object {
        /**
         * Display instance.
         */
        public Gdk.Display display { get; construct; }

        /**
         * Signal emitted when modifiers have changed.
         */
        public signal void modifiers_changed (uint modifiers);

        /**
         * Signal emitted when the current group has changed.
         *
         * @param gid group index
         * @param group group name
         * @param variant variant name
         */
        public signal void group_changed (uint gid,
                                          string group,
                                          string variant);

        /**
         * Signal emitted when the group configuration has changed.
         */
        public signal void config_changed ();

        /**
         * Send key press event.
         *
         * @param keyval keyval
         */
        public abstract void keyval_press (uint keyval);

        /**
         * Send key release event.
         *
         * @param keyval keyval
         */
        public abstract void keyval_release (uint keyval);

        /**
         * Lock modifiers.
         *
         * @param mask modifiers
         */
        public abstract void mod_lock (uint mask);

        /**
         * Unlock modifiers.
         *
         * @param mask modifiers
         */
        public abstract void mod_unlock (uint mask);

        /**
         * Latch modifiers.
         *
         * @param mask modifiers
         */
        public abstract void mod_latch (uint mask);

        /**
         * Unlatch modifiers.
         *
         * @param mask modifiers
         */
        public abstract void mod_unlatch (uint mask);

        /**
         * Get the current group.
         *
         * @param group_name group name
         * @param variant_name variant name
         */
        public abstract uint get_current_group (out string group_name,
                                                out string variant_name);

        /**
         * Get available groups.
         *
         * @param group_names list of groups
         * @param variant_names list of variants, indexed same as group_names
         */
        public abstract void get_groups (out string[] group_names,
                                         out string[] variant_names);

        /**
         * Register key callback.
         *
         * @param keyval keyval
         * @param func callback
         */
        public abstract void register_key_func (uint keyval,
                                                KeyButtonCallback? func);

        /**
         * Register button callback.
         *
         * @param button button
         * @param func callback
         */
        public abstract void register_button_func (uint button,
                                                   KeyButtonCallback? func);

        static DisplayAdapter instance;
        public static bool set_default (DisplayAdapter adapter) {
            if (instance != null)
                return false;

            instance = adapter;
            return true;
        }
        public static DisplayAdapter get_default () {
            if (instance == null) {
                var display = Gdk.DisplayManager.get ().get_default_display ();
                var adapter_type = typeof (NullAdapter);
                if (display != null) {
                    var adapters = new Gee.HashMap<Type, Type> ();
                    adapters.set (typeof (Gdk.X11Display), typeof (XAdapter));

                    var display_type = display.get_type ();
                    if (adapters.has_key (display_type))
                        adapter_type = adapters.get (display_type);
                }
                instance = (DisplayAdapter) Object.new (adapter_type,
                                                        "display", display);
            }
            return instance;
        }
    }

    public class NullAdapter : DisplayAdapter {
        public override void keyval_press (uint keyval) {
        }

        public override void keyval_release (uint keyval) {
        }

        public override void mod_lock (uint mask) {
        }

        public override void mod_unlock (uint mask) {
        }

        public override void mod_latch (uint mask) {
        }

        public override void mod_unlatch (uint mask) {
        } 

        public override uint get_current_group (out string group_name,
                                                out string variant_name)
        {
            group_name = "us";
            variant_name = "";
            return 0;
        }

        public override void get_groups (out string[] group_names,
                                         out string[] variant_names)
        {
            group_names = new string[] { "us" };
            variant_names = new string[] { "" };
        }

        public override void register_key_func (uint keyval,
                                                KeyButtonCallback? func)
        {
        }

        public override void register_button_func (uint button,
                                                   KeyButtonCallback? func)
        {
        }
    }
}
