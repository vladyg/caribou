namespace Caribou {
    [DBus(name = "org.gnome.Caribou.Keyboard")]
    interface Keyboard : Object {
        public abstract void set_cursor_location (int x, int y, int w, int h) throws IOError;
        public abstract void set_entry_location (int x, int y, int w, int h) throws IOError;
        public abstract void show () throws IOError;
        public abstract void hide () throws IOError;
    }

    class IMContext : Gtk.IMContextSimple {
        private Gdk.Window window;
        private Keyboard keyboard;

        public IMContext () {
        }

        public override void focus_in () {
            int x, y, w, h;
            window.get_origin (out x, out y);
#if GTK2
            window.get_geometry (null, null, out w, out h, null);
#else
            window.get_geometry (null, null, out w, out h);
#endif
            stdout.printf ("focus_in %d %d\n", x, y);
            try {
                keyboard.show ();
                keyboard.set_entry_location (x, y, w, h);
            } catch (IOError e) {
                stderr.printf ("%s\n", e.message);
            }
        }

        public override void focus_out () {
            try {
                keyboard.hide ();
            } catch (IOError e) {
                stderr.printf ("%s\n", e.message);
            }
        }

        public override void set_client_window (Gdk.Window window) {
            this.window = window;
            try {
                keyboard = Bus.get_proxy_sync (BusType.SESSION,
                                               "org.gnome.Caribou.Antler",
                                               "/org/gnome/Caribou/Antler");
            } catch (Error e) {
                stderr.printf ("%s\n", e.message);
            }
            stdout.printf ("set_client_window\n");
        }
    }
}