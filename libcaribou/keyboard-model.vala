using Bus;

namespace Caribou {
    public class KeyboardModel : Object {
        public string active_group { get; private set; default = ""; }

        XAdapter xadapter;
        HashTable<string, GroupModel> groups;

        construct {
            uint grpid;
            string group, variant;
            string[] grps, variants;
            int i;

            groups = new HashTable<string, GroupModel> (str_hash, str_equal);

            xadapter = XAdapter.get_default ();
            xadapter.group_changed.connect (on_group_changed);

            grpid = xadapter.get_current_group (out group, out variant);
            on_group_changed (grpid, group, variant);

            xadapter.get_groups (out grps, out variants);

            for (i=0;i<grps.length;i++)
                populate_group (grps[i], variants[i]);
        }

        private void populate_group (string group, string variant) {
            GroupModel grp = new GroupModel (group, variant);
            groups.insert (GroupModel.create_group_name (group, variant), grp);
            JsonDeserializer.load_group (grp);
        }

        public string[] get_groups () {
            return Util.list_to_array (groups.get_keys ());
        }

        public GroupModel get_group (string group_name) {
            return groups.lookup(group_name);
        }

        private void on_group_changed (uint grpid, string group, string variant) {
            active_group = group;
        }

    }
}