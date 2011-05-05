using GLib;

namespace Caribou {
    public class LevelModel : GLib.Object {
        public signal void level_toggled (string new_level);

        public string mode { get; private set; default = ""; }
        public int n_rows {
            get {
                return _rows.length;
            }
        }

        private RowModel[] _rows;

        public LevelModel (string mode, uint nrows) {
            uint i;
            this.mode = mode;
            _rows = new RowModel[nrows];
            for (i=0;i<nrows;i++)
                _rows[i] = new RowModel ();
        }

        public void add_key (uint rownum, KeyModel key) {
            key.key_clicked.connect (on_key_clicked);
            _rows[rownum].add_key (key);
        }

        public RowModel[] get_rows () {
            return _rows;
        }

        private void on_key_clicked (KeyModel key) {
            if (key.toggle != "")
                level_toggled (key.toggle);
            else if (mode == "latched")
                level_toggled ("default");
        }

    }
}