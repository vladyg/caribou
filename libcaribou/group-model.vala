using GLib;

namespace Caribou {
    public class GroupModel : GLib.Object {
        public string active_level { get; private set; }

        public string group;
        public string variant;
        private string default_level;
        private HashTable<string, LevelModel> levels;

        public GroupModel (string group, string variant) {
            this.group = group;
            this.variant = variant;
            levels = new HashTable<string, LevelModel> (str_hash, str_equal);
            active_level = default_level;
        }

        public static string create_group_name (string group, string variant) {
            if (variant != "")
                return @"$(group)_$(variant)";
            else
                return group;
        }

        internal void add_level (string lname, LevelModel level) {
            levels.insert (lname, level);
            level.level_toggled.connect(on_level_toggled);
            if (level.mode == "default") {
                default_level = lname;
                active_level = lname;
            }
        }

        public string[] get_levels () {
            return Util.list_to_array (levels.get_keys ());
        }

        public LevelModel get_level (string level_name) {
            return levels.lookup(level_name);
        }

        private void on_level_toggled (string new_level) {
            if (new_level == "default")
                active_level = default_level;
            else
                active_level = new_level;
        }
    }
}