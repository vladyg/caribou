namespace Caribou {
    /**
     * Object representing a whole keyboard.
     *
     * This is used for implementing custom keyboard service.
     *
     * A keyboard object consists of {@link GroupModel} objects.
     */
    public class KeyboardModel : Object, IKeyboardObject {
        public string active_group { get; private set; default = ""; }
        public string keyboard_type { get; construct; }

        private DisplayAdapter xadapter;
        private Gee.HashMap<string, GroupModel> groups;
        private KeyModel last_activated_key;
        private Gee.HashSet<KeyModel> active_mod_keys;

        public signal void group_added (string name);
        public signal void group_removed (string name);

        construct {
            assert (keyboard_type != null);

            xadapter = DisplayAdapter.get_default ();
            xadapter.group_changed.connect (on_group_changed);
            xadapter.config_changed.connect (on_config_changed);

            groups = new Gee.HashMap<string, GroupModel> ();
            on_config_changed ();

            active_mod_keys = new Gee.HashSet<KeyModel> ();
        }

        private void on_config_changed () {
            string[] grps, variants;
            xadapter.get_groups (out grps, out variants);

            var group_names = new Gee.HashSet<string> ();
            for (var i = 0; i < grps.length; i++) {
                var group_name = GroupModel.create_group_name (grps[i],
                                                               variants[i]);
                group_names.add (group_name);
                if (!groups.has_key (group_name)) {
                    var grp = populate_group (grps[i], variants[i]);
                    if (grp != null) {
                        groups.set (group_name, grp);
                        group_added (group_name);
                    }
                }
            }

            var iter = groups.map_iterator ();
            while (iter.next ()) {
                var group_name = iter.get_key ();
                if (!group_names.contains (group_name)) {
                    iter.unset ();
                    group_removed (group_name);
                }
            }

            string group, variant;
            var grpid = xadapter.get_current_group (out group, out variant);
            on_group_changed (grpid, group, variant);
        }

        private GroupModel? populate_group (string group, string variant) {
            GroupModel grp = XmlDeserializer.load_group (keyboard_type,
                                                         group, variant);
            if (grp != null) {
                grp.key_clicked.connect (on_key_clicked);
                grp.key_pressed.connect (on_key_pressed);
                grp.key_released.connect (on_key_released);
            }
            return grp;
        }

        private void on_key_clicked (KeyModel key) {
            if (key.name == "Caribou_Repeat")
                last_activated_key.activate ();
            else
                last_activated_key = key;

            key_clicked (key);
        }

        private void on_key_pressed (KeyModel key) {
            if (key.is_modifier && key.modifier_state == ModifierState.LATCHED) {
                active_mod_keys.add(key);
            }
        }

        private void on_key_released (KeyModel key) {
            if (!key.is_modifier) {
                KeyModel[] modifiers = (KeyModel[]) active_mod_keys.to_array ();
                foreach (KeyModel modifier in modifiers) {
                    if (modifier.modifier_state == ModifierState.LATCHED) {
                        modifier.modifier_state = ModifierState.NONE;
                        modifier.release ();
                    }
                }
            }
        }

        public string[] get_groups () {
            return (string[]) groups.keys.to_array ();
        }

        public GroupModel get_group (string group_name) {
            return groups.get (group_name);
        }

        private void on_group_changed (uint grpid, string group, string variant) {
            string group_name = GroupModel.create_group_name (group, variant);
            if (groups.get (group_name) != null) {
                active_group = group_name;
            } else {
                active_group = get_groups ()[0];
            }
        }

        public IKeyboardObject[] get_children () {
            return (IKeyboardObject[]) groups.values.to_array ();
        }
    }
}
