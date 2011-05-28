namespace Caribou {
    public class ColumnModel : Object {
        Gee.ArrayList<KeyModel> keys;

        public ColumnModel () {
            keys = new Gee.ArrayList<KeyModel> ();
        }

        internal void add_key (KeyModel key) {
            keys.add (key);
        }

        public KeyModel get_key (int index) {
            return keys.get (index);
        }

        public KeyModel[] get_keys () {
            return (KeyModel[]) keys.to_array ();
        }

        public KeyModel first_key () {
            return keys.first();
        }
   }
}
