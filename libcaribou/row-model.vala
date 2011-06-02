namespace Caribou {
    public class RowModel : ScannableGroup, IScannableItem, IKeyboardObject {
        public bool scan_stepping { get; set; }
        public bool scan_selected { get; set; }

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
                column.key_activated.connect ((k) => { key_activated (k); });
                columns.add(column);
            } else {
                column = columns[colindex];
            }

            column.add_key (key);
        }

        public List<ColumnModel> get_columns () {
            return (List<ColumnModel>) get_children ();
        }

        public override IScannableItem[] get_scan_children () {
            if (scan_grouping == ScanGrouping.ROWS)
                return (IScannableItem[]) get_keys ();
            else
                return (IScannableItem[]) columns.to_array ();
        }

        public List<IKeyboardObject> get_children () {
            return (List<IKeyboardObject>) collection_to_object_list (columns);
        }
    }
}
