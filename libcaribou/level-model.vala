using GLib;

namespace Caribou {
    public class LevelModel : GLib.Object {
        public signal void level_toggled (string new_level);
        public string mode { get; private set; default = ""; }

        private Gee.ArrayList<RowModel> rows;

        public LevelModel (string mode) {
            this.mode = mode;
            rows = new Gee.ArrayList<RowModel> ();
        }

        internal void add_key (int rownum, int colnum, KeyModel key) {
            int rowindex = rownum;
            RowModel row = null;

            if (rownum < 0)
                rowindex = rows.size + rownum;

            if (rownum >= rows.size) {
                row = new RowModel ();
                rows.add(row);
            } else {
                row = rows[rowindex];
            }

            row.add_key (colnum, key);

            key.key_clicked.connect (on_key_clicked);
        }

        public RowModel[] get_rows () {
            return (RowModel[]) rows.to_array ();
        }

        private void on_key_clicked (KeyModel key) {
            if (key.toggle != "")
                level_toggled (key.toggle);
            else if (mode == "latched")
                level_toggled ("default");
        }

        public KeyModel[] get_keys () {
            Gee.ArrayList<KeyModel> keys = new Gee.ArrayList<KeyModel> ();
            foreach (RowModel row in rows) {
                KeyModel[] row_keys = row.get_keys();
                foreach (KeyModel key in row_keys) {
                    keys.add(key);
                }
            }

            return (KeyModel[]) keys.to_array ();
        }
    }
}