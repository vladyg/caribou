using GLib;

namespace Caribou {
    public class KeyModel : GLib.Object {
        public double margin_left { get; set; default = 0.0; }
        public double width { get; set; default = 1.0; }
        public string toggle { get; set; default = ""; }

        public bool show_subkeys { get; private set; default = false; }
        public string name { get; private set; }
        public uint keyval { get; private set; }

        private uint hold_tid;
        private XAdapter xadapter;
        private Gee.ArrayList<KeyModel> extended_keys;

        public signal void key_pressed ();
        public signal void key_released ();
        public signal void key_clicked ();
        public signal void key_hold_end ();
        public signal void key_hold ();

        public KeyModel (string name) {
            this.name = name;
            xadapter = XAdapter.get_default();
            keyval = Gdk.keyval_from_name (name);
            extended_keys = new Gee.ArrayList<KeyModel> ();
        }

        internal void add_subkey (string name) {
            KeyModel key = new KeyModel (name);
            key.key_clicked.connect(on_subkey_clicked);
            extended_keys.add (key);
        }

        private void on_subkey_clicked () {
            show_subkeys = false;
        }

        public void press () {
            hold_tid = GLib.Timeout.add(1000, on_key_held);
            key_pressed();
        }

        public void release () {
            key_released();
            if (hold_tid != 0) {
                GLib.Source.remove (hold_tid);
                hold_tid = 0;
                key_clicked();
                if (keyval != 0) {
                    xadapter.keyval_press(keyval);
                    xadapter.keyval_release(keyval);
                }
            } else {
                key_hold_end ();
            }
        }

        private bool on_key_held () {
            hold_tid = 0;
            if (extended_keys.size != 0)
                show_subkeys = true;
            key_hold ();
            return false;
        }

        public KeyModel[] get_extended_keys () {
            return (KeyModel[]) extended_keys.to_array ();
        }
    }
}