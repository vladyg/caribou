namespace Caribou {
    public interface IScannableGroup : Object {
        public abstract IScannableItem? child_select ();
        public abstract void scan_reset ();
        public abstract IScannableItem[] get_scan_children ();
        public abstract IScannableItem? child_step (int cycles);
        public abstract IScannableItem[] get_step_path ();
        public abstract IScannableItem[] get_selected_path ();

        public abstract ScanGrouping scan_grouping { get; set; }

        public signal void selected_item_changed (IScannableItem? selected_item);
        public signal void step_item_changed (IScannableItem? step_item);
        public signal void scan_cleared ();
    }

    public enum ScanGrouping {
        NONE,
        SUBGROUPS,
        ROWS,
        LINEAR
    }
}