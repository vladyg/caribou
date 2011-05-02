namespace Caribou {
    public class RowModel : GLib.Object {

        List<KeyModel> keys;

        public RowModel () {
            keys = new List<KeyModel> ();
        }

        public void add_key (KeyModel key) {
            keys.append (key);
        }

        public KeyModel get_key (uint index) {
            return keys.nth (index).data;
        }

        public unowned List<weak KeyModel> get_keys () {
            return keys;
        }
    }
}
