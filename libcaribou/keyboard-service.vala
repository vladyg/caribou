namespace Caribou {
    [DBus(name = "org.gnome.Caribou.Keyboard")]
    public abstract class KeyboardService : Object {
        public string name { get; private set; default = "CaribouKeyboard"; }

        public abstract void set_cursor_location(int x, int y, int w, int h);
        public abstract void set_entry_location(int x, int y, int w, int h);
        public abstract void show();
        public abstract void hide();

        protected void register_keyboard (string name) {
            this.name = name;
            string dbus_name = @"org.gnome.Caribou.$name";
            Bus.own_name (BusType.SESSION, dbus_name, BusNameOwnerFlags.NONE,
                          on_bus_aquired, on_name_aquired, on_name_lost);
        }

        private void on_name_aquired (DBusConnection conn, string name) {
        }

        private void on_name_lost (DBusConnection conn, string name) {
            stderr.printf ("Could not aquire %s\n", name);
        }

        private void on_bus_aquired (DBusConnection conn) {
            try {
                string path = @"/org/gnome/Caribou/$name";
                conn.register_object (path, this);
            } catch (IOError e) {
                stderr.printf ("Could not register service: %s\n", e.message);
            }
        }

    }
}