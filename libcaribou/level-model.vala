using GLib;

namespace Caribou {
    public class LevelModel : ScannableGroup, IKeyboardObject {
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
                row.key_activated.connect (on_key_activated);
                rows.add(row);
            } else {
                row = rows[rowindex];
            }

            row.add_key (colnum, key);
        }

        public List<RowModel> get_rows () {
            return (List<RowModel>) get_children ();
        }

        private void on_key_activated (KeyModel key) {
            if (key.toggle != "")
                level_toggled (key.toggle);
            else if (mode == "latched")
                level_toggled ("default");
            key_activated (key);
        }

        public override IScannableItem[] get_scan_children () {
            if (scan_grouping == ScanGrouping.LINEAR)
                return (IScannableItem[]) get_keys ();
            else
                return (IScannableItem[]) rows.to_array ();
        }

        public List<IKeyboardObject> get_children () {
            return (List<IKeyboardObject>) collection_to_object_list (rows);
        }
    }
}
