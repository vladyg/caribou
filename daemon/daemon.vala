namespace Caribou {
    // We can't use the name "Keyboard" here since caribou-gtk-module
    // might register the name first.
    [DBus (name = "org.gnome.Caribou.Keyboard")]
    interface _Keyboard : Object {
        public abstract void set_cursor_location (int x, int y, int w, int h)
            throws IOError;
        public abstract void set_entry_location (int x, int y, int w, int h)
            throws IOError;
        public abstract void show (uint32 timestamp) throws IOError;
        public abstract void hide (uint32 timestamp) throws IOError;
    }

    [DBus (name = "org.gnome.Caribou.Daemon")]
    class Daemon : Object {
        _Keyboard keyboard;
        Atspi.Accessible current_acc;
        unowned Gdk.Display display;
        uint name_id;

        public Daemon () {
            display = Gdk.Display.get_default ();
            name_id = Bus.own_name (BusType.SESSION,
                                    "org.gnome.Caribou.Daemon",
                                    BusNameOwnerFlags.ALLOW_REPLACEMENT
                                    | BusNameOwnerFlags.REPLACE,
                                    on_bus_acquired, null, quit);
        }

        ~Daemon () {
            Bus.unown_name (name_id);
        }

        void on_bus_acquired (DBusConnection conn) {
            try {
                conn.register_object ("/org/gnome/Caribou/Daemon", this);
            } catch (IOError e) {
                error ("Could not register D-Bus service: %s", e.message);
            }
        }

        void on_get_proxy_ready (GLib.Object? obj, GLib.AsyncResult res) {
            try {
                keyboard = Bus.get_proxy.end (res);
            } catch (Error e) {
                error ("%s\n".printf (e.message));
            }

            try {
                register_event_listeners ();
            } catch (Error e) {
                warning ("can't register event listeners: %s", e.message);
            }
        }

        uint32 get_timestamp () {
            if (display is Gdk.X11Display)
                return Gdk.X11Display.get_user_time (display);
            else
                return 0;
        }

        void set_entry_location (Atspi.Accessible acc) throws Error {
            var text = acc.get_text ();
            var rect = text.get_character_extents (text.get_caret_offset (),
                                                   Atspi.CoordType.SCREEN);
            var component = acc.get_component ();
            var entry_rect = component.get_extents (Atspi.CoordType.SCREEN);
            if (rect.x == 0 && rect.y == 0 &&
                rect.width == 0 && rect.height == 0) {
                rect = entry_rect;
            }

            keyboard.set_cursor_location (rect.x, rect.y,
                                          rect.width, rect.height);

            keyboard.set_entry_location (entry_rect.x, entry_rect.y,
                                         entry_rect.width, entry_rect.height);

            keyboard.show (get_timestamp ());
        }

        void on_focus (owned Atspi.Event event) throws Error {
            var acc = event.source;
            var source_role = acc.get_role ();
            if (acc.get_state_set ().contains (Atspi.StateType.EDITABLE) ||
                source_role == Atspi.Role.TERMINAL) {
                switch (source_role) {
                case Atspi.Role.TEXT:
                case Atspi.Role.PARAGRAPH:
                case Atspi.Role.PASSWORD_TEXT:
                case Atspi.Role.TERMINAL:
                case Atspi.Role.ENTRY:
                    if (event.type == "object:state-changed:focused") {
                        if (event.detail1 == 1) {
                            set_entry_location (acc);
                            current_acc = event.source;
                            debug ("enter text widget in %s",
                                   event.source.get_application ().name);
                        } else if (acc == current_acc) {
                            keyboard.hide (get_timestamp ());
                            current_acc = null;
                            debug ("leave text widget in %s",
                                   event.source.get_application ().name);
                        }
                    } else {
                        warning ("unknown focus event: %s", event.type);
                    }
                    break;
                default:
                    break;
                }
            }
        }

        void on_focus_ignore_error (owned Atspi.Event event) {
            try {
                on_focus (event);
            } catch (Error e) {
                warning ("error in focus handler: %s", e.message);
            }
        }

        void on_text_caret_moved (owned Atspi.Event event) throws Error {
            if (current_acc == event.source) {
                var text = current_acc.get_text ();
                var rect = text.get_character_extents (text.get_caret_offset (),
                                                       Atspi.CoordType.SCREEN);
                if (rect.x == 0 && rect.y == 0 &&
                    rect.width == 0 && rect.height == 0) {
                    var component = current_acc.get_component ();
                    rect = component.get_extents (Atspi.CoordType.SCREEN);
                }

                keyboard.set_cursor_location (rect.x, rect.y,
                                              rect.width, rect.height);
                debug ("object:text-caret-moved in %s: %d %s",
                       event.source.get_application ().name,
                       event.detail1, event.source.description);
            }
        }

        void on_text_caret_moved_ignore_error (owned Atspi.Event event) {
            try {
                on_text_caret_moved (event);
            } catch (Error e) {
                warning ("error in text caret movement handler: %s", e.message);
            }
        }

        void register_event_listeners () throws Error {
            Atspi.EventListener.register_from_callback (
                on_focus_ignore_error, "object:state-changed:focused");
            Atspi.EventListener.register_from_callback (
                on_text_caret_moved_ignore_error, "object:text-caret-moved");
        }

        void deregister_event_listeners () throws Error {
            Atspi.EventListener.deregister_from_callback (
                on_focus_ignore_error, "object:state-changed:focused");
            Atspi.EventListener.deregister_from_callback (
                on_text_caret_moved_ignore_error, "object:text-caret-moved");
        }

        [DBus (name = "Run")]
        public void ping () {
            // This method is called over D-Bus, upon activation.
        }

        [DBus (visible = false)]
        public void run () {
            Bus.get_proxy.begin<_Keyboard> (BusType.SESSION,
                                            "org.gnome.Caribou.Keyboard",
                                            "/org/gnome/Caribou/Keyboard",
                                            0,
                                            null,
                                            on_get_proxy_ready);
            // Use Atspi.Event.{main,quit}, instead of GLib.MainLoop
            // to enable property caching in libatspi.
            Atspi.Event.main ();
        }

        public void quit () {
            if (keyboard != null) {
                try {
                    keyboard.hide (get_timestamp ());
                } catch (IOError e) {
                    warning ("can't hide keyboard: %s", e.message);
                }

                try {
                    deregister_event_listeners ();
                } catch (Error e) {
                    warning ("can't deregister event listeners: %s", e.message);
                }
                keyboard = null;
            }

            Atspi.Event.quit ();
        }
    }
}

static const OptionEntry[] options = {
    { null }
};

static int main (string[] args) {
    Gdk.init (ref args);

    Intl.setlocale (LocaleCategory.ALL, "");
    Intl.bindtextdomain (Config.GETTEXT_PACKAGE, Config.LOCALEDIR);
    Intl.bind_textdomain_codeset (Config.GETTEXT_PACKAGE, "UTF-8");
    Intl.textdomain (Config.GETTEXT_PACKAGE);

    var option_context = new OptionContext (_(
        "— accessibility event monitoring daemon for screen keyboard"));
    option_context.add_main_entries (options, "caribou");
    try {
        option_context.parse (ref args);
    } catch (OptionError e) {
        stderr.printf ("%s\n", e.message);
        return 1;
    }

    var retval = Atspi.init ();
    if (retval != 0) {
        printerr ("can't initialize atspi\n");
        return 1;
    }

    var daemon = new Caribou.Daemon ();
    Unix.signal_add (Posix.SIGINT, () => {
            daemon.quit ();
            return false;
        });
    daemon.run ();

    return 0;
}
