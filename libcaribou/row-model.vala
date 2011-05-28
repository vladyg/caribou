namespace Caribou {
    public class RowModel : GLib.Object {

        Gee.ArrayList<ColumnModel> columns;

        public RowModel () {
            columns = new Gee.ArrayList<ColumnModel> ();
        }

        internal void add_key (int colnum, KeyModel key) {
            int colindex = colnum;
            ColumnModel column = null;

            if (colnum < 0)
                colindex = columns.size + colnum;

            if (colnum >= columns.size) {
                column = new ColumnModel ();
                columns.add(column);
            } else {
                column = columns[colindex];
            }

            column.add_key (key);
        }

        public KeyModel[] get_keys () {
            Gee.ArrayList<KeyModel> keys = new Gee.ArrayList<KeyModel> ();
            foreach (ColumnModel column in columns) {
                KeyModel[] col_keys = column.get_keys();
                foreach (KeyModel key in col_keys) {
                    keys.add(key);
                }
            }
            return (KeyModel[]) keys.to_array ();
        }

        public ColumnModel[] get_columns () {
            return (ColumnModel[]) columns.to_array ();
        }

    }
}
