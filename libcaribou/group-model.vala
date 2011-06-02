using GLib;

namespace Caribou {
    public class GroupModel : Object, IKeyboardObject {
        public string active_level { get; private set; }

        public string group;
        public string variant;
        private string default_level;
        private Gee.HashMap<string, LevelModel> levels;

        public GroupModel (string group, string variant) {
            this.group = group;
            this.variant = variant;
            levels = new Gee.HashMap<string, LevelModel> (str_hash, str_equal);
            active_level = default_level;
        }

        public static string create_group_name (string group, string variant) {
            if (variant != "")
                return @"$(group)_$(variant)";
            else
                return group;
        }

        internal void add_level (string lname, LevelModel level) {
            levels.set (lname, level);
            level.level_toggled.connect (on_level_toggled);
            level.key_activated.connect ((k) => { key_activated (k); });
            if (level.mode == "default") {
                default_level = lname;
                active_level = lname;
            }
        }

        public List<string> get_levels () {
            return (List<string>) collection_to_string_list (levels.keys);
        }

        public LevelModel get_level (string level_name) {
            return levels.get (level_name);
        }

        private void on_level_toggled (string new_level) {
            if (new_level == "default")
                active_level = default_level;
            else
                active_level = new_level;
        }

        public List<IKeyboardObject> get_children () {
            return (List<IKeyboardObject>)
                collection_to_object_list (levels.values);
        }
    }
}