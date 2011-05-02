namespace Caribou {

    private class JsonDeserializer : Object {

        public static bool get_layout_file_inner (string data_dir,
                                                  string group,
                                                  string variant,
                                                  out File fp) {
            string[] files = {@"$(group)_$(variant).json", @"$(group).json"};

            foreach (string fn in files) {
                string layout_fn = GLib.Path.build_filename (data_dir, fn);
                fp = GLib.File.new_for_path (layout_fn);
                if (fp.query_exists ())
                    return true;
            }

            return false;
        }

        public static GLib.File get_layout_file (string group,
                                                 string variant) throws IOError {
            Settings caribou_settings = new Settings ("org.gnome.caribou");
            string kb_type = caribou_settings.get_string("keyboard-type");

            List<string> dirs = new List<string> ();
            string custom_dir = Environment.get_variable("CARIBOU_LAYOUTS_DIR");

            if (custom_dir != null)
                dirs.append (Path.build_filename (custom_dir, "layouts", kb_type));

            dirs.append (Path.build_filename (Environment.get_user_data_dir (),
                                              "caribou", "layouts", kb_type));

            foreach (string data_dir in Environment.get_system_data_dirs ()) {
                dirs.append (Path.build_filename (
                                 data_dir, "caribou", "layouts", kb_type));
            }

            foreach (string data_dir in dirs) {
                File fp;
                if (get_layout_file_inner (data_dir, group, variant, out fp))
                    return fp;
            }

            throw new IOError.NOT_FOUND (
                "Could not find layout file for %s %s", group, variant);                       }

        public static void load_group (GroupModel group) {
            Json.Parser parser = new Json.Parser ();

            try {
                GLib.File f = get_layout_file (group.group, group.variant);
                parser.load_from_stream (f.read (), (Cancellable) null);
                create_levels_from_json (group, parser.get_root ());
            } catch (GLib.Error e) {
                stdout.printf ("Failed to load JSON: %s\n", e.message);
                return;
            }
        }

        public static void create_levels_from_json (GroupModel group,
                                                    Json.Node root) {
            Json.Object obj = root.get_object ();

            if (root.get_node_type () != Json.NodeType.OBJECT)
                return;

            foreach (string levelname in obj.get_members ()) {
                unowned Json.Object json_level = obj.get_object_member (levelname);
                string mode = "";

                if (json_level.has_member ("mode"))
                    mode = json_level.get_string_member ("mode");

                Json.Array json_rows = json_level.get_array_member ("rows");
                LevelModel level = new LevelModel(mode, json_rows.get_length ());

                group.add_level(levelname, level);

                load_rows (level, json_rows);
            }
        }

        public static void load_rows (LevelModel level, Json.Array json_rows) {
            uint i,j;

            for (i=0;i<level.n_rows;i++) {
                Json.Array json_keys = json_rows.get_array_element (i);
                uint nkeys = json_keys.get_length ();
                for (j=0;j<nkeys;j++) {
                    Json.Object json_key = json_keys.get_object_element (j);
                    level.add_key (i, load_key (json_key));
                }
            }

        }

        public static KeyModel load_key (Json.Object json_key) {
            KeyModel key = new KeyModel (json_key.get_string_member ("name"));

            if (json_key.has_member ("toggle"))
                key.toggle = json_key.get_string_member ("toggle");

            if (json_key.has_member ("margin_left"))
                key.margin_left = json_key.get_double_member ("margin_left");

            if (json_key.has_member ("width"))
                key.width = json_key.get_double_member ("width");

            if (json_key.has_member ("extended_names")) {
                Json.Array json_keys = json_key.get_array_member ("extended_names");
                uint nkeys = json_keys.get_length ();
                uint i;

                key.add_subkey(key.name);

                for (i=0;i<nkeys;i++)
                    key.add_subkey(json_keys.get_string_element (i));
            }

            return key;
        }
        
    }
}