namespace Caribou {
    public interface IKeyboardObject : Object {
        public abstract IKeyboardObject[] get_children ();

        public signal void key_activated (KeyModel key);

        public virtual KeyModel[] get_keys () {
            Gee.ArrayList<KeyModel> keys = new Gee.ArrayList<KeyModel> ();
            foreach (IKeyboardObject obj in get_children ()) {
                KeyModel[] obj_keys = obj.get_keys();
                foreach (KeyModel key in obj_keys) {
                    keys.add(key);
                }
            }
            return (KeyModel[]) keys.to_array ();
        }
    }
}