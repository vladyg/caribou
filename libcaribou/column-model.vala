namespace Caribou {
    public class ColumnModel : ScannableGroup, IScannableItem, IKeyboardObject {
        public bool scan_stepping { get; set; }
        public bool scan_selected { get; set; }

        Gee.ArrayList<KeyModel> keys;

        public ColumnModel () {
            keys = new Gee.ArrayList<KeyModel> ();
        }

        internal void add_key (KeyModel key) {
            key.key_activated.connect ((k) => { key_activated (k); });
            keys.add (key);
        }

        public KeyModel get_key (int index) {
            return keys.get (index);
        }

        public KeyModel first_key () {
            return keys.first();
        }

        public override IScannableItem[] get_scan_children () {
            return (IScannableItem[]) keys.to_array ();
        }

        public IKeyboardObject[] get_children () {
            return (IKeyboardObject[]) keys.to_array ();
        }
    }
}
