using Bus;

namespace Caribou {
    public class KeyboardModel : Object, IKeyboardObject {
        public string active_group { get; private set; default = ""; }
        public string keyboard_type { get; construct; }

        XAdapter xadapter;
        HashTable<string, GroupModel> groups;

        construct {
            uint grpid;
            string group, variant;
            string[] grps, variants;
            int i;

            assert (keyboard_type != null);

            xadapter = XAdapter.get_default ();
            xadapter.group_changed.connect (on_group_changed);

            xadapter.get_groups (out grps, out variants);

            groups = new HashTable<string, GroupModel> (str_hash, str_equal);

            for (i=0;i<grps.length;i++)
                populate_group (grps[i], variants[i]);

            grpid = xadapter.get_current_group (out group, out variant);
            on_group_changed (grpid, group, variant);
        }

        private void populate_group (string group, string variant) {
            GroupModel grp = JsonDeserializer.load_group (keyboard_type,
                                                          group, variant);
            if (grp != null)
                groups.insert (GroupModel.create_group_name (group, variant), grp);
        }

        public string[] get_groups () {
            return Util.list_to_array (groups.get_keys ());
        }

        public GroupModel get_group (string group_name) {
            return groups.lookup (group_name);
        }

        private void on_group_changed (uint grpid, string group, string variant) {
            string group_name = GroupModel.create_group_name (group, variant);
            if (groups.lookup (group_name) != null) {
                active_group = group_name;
            } else {
                active_group = get_groups ()[0];
            }
        }

        public IKeyboardObject[] get_children () {
            IKeyboardObject[] children = new IKeyboardObject[groups.size ()];
            uint i = 0;

            foreach (GroupModel obj in groups.get_values ()) {
                children[i++] = (IKeyboardObject) obj;
            }

            return children;
        }
    }
}