namespace Caribou {
    public interface IKeyboardObject : Object {
        public abstract List<IKeyboardObject> get_children ();

        public signal void key_activated (KeyModel key);

        public virtual List<KeyModel> get_keys () {
            var keys = new List<KeyModel> ();
            foreach (IKeyboardObject obj in get_children ()) {
                List<weak KeyModel> child_keys = obj.get_keys();
                keys.concat (child_keys.copy());
            }
            return keys;
        }

        internal static List<Object> collection_to_object_list (Gee.Collection<Object> c) {
            var l = new List<Object> ();
            foreach (Object item in c) {
                l.append (item);
            }
            return l;
        }

        internal static List<string> collection_to_string_list (Gee.Collection<string> c) {
            List<string> l = new List<string> ();
            foreach (string item in c) {
                l.append (item);
            }
            return l;
        }
    }
}