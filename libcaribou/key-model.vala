using GLib;

namespace Caribou {
    public class KeyModel : GLib.Object, IScannableItem, IKeyboardObject {
        public double margin_left { get; set; default = 0.0; }
        public double width { get; set; default = 1.0; }
        public string toggle { get; set; default = ""; }

        public bool show_subkeys { get; private set; default = false; }
        public string name { get; private set; }
        public uint keyval { get; private set; }

        public bool scan_stepping { get; internal set; }
        private bool _scan_selected;
        public bool scan_selected {
            get {
                return _scan_selected;
            }

            internal set {
                _scan_selected = value;
                if (_scan_selected)
                    activate ();
            }
        }

        private uint hold_tid;
        private XAdapter xadapter;
        private Gee.ArrayList<KeyModel> extended_keys;

        public signal void key_pressed ();
        public signal void key_released ();
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
            key.key_activated.connect(on_subkey_activated);
            extended_keys.add (key);
        }

        private void on_subkey_activated (KeyModel key) {
            key_activated (key);
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
                key_activated (this);
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

        public List<KeyModel> get_extended_keys () {
            return (List<KeyModel>) collection_to_object_list(extended_keys);
        }

        public List<KeyModel> get_keys () {
            List<KeyModel> all_keys = new List<KeyModel> ();
            all_keys.append (this);
            var ekeys = (List<weak KeyModel>) get_extended_keys ();
            all_keys.concat (ekeys.copy());
            return all_keys;
        }

        public List<IKeyboardObject> get_children () {
            return (List<IKeyboardObject>)
                collection_to_object_list (extended_keys);
        }

        public void activate () {
            press ();
            GLib.Timeout.add(100, () => { release (); return false; });
        }
    }
}