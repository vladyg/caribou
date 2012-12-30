namespace Caribou {
    /**
     * Base abstract class that implements scanning mode containers.
     */
    public abstract class ScannableGroup : Object, IScannableGroup {
        private Gee.LinkedList<IScannableItem> _step_path;
        private Gee.LinkedList<IScannableItem> _selected_path;
        private int _cycle_count;

        private ScanGrouping _scan_grouping;
        public ScanGrouping scan_grouping {
            get {
                return _scan_grouping;
            }

            set {
                _scan_grouping = value;
                foreach (IScannableItem item in get_scan_children ()) {
                    if (item is IScannableGroup)
                        ((IScannableGroup) item).scan_grouping = value;
                }
            }
        }

        private int scan_child_index { get; set; default=-1; }

        public abstract IScannableItem[] get_scan_children ();

        construct {
            _step_path = new Gee.LinkedList<IScannableItem> ();
            _selected_path = new Gee.LinkedList<IScannableItem> ();
        }

        public IScannableItem[] get_step_path () {
            return (IScannableItem[]) _step_path.to_array ();
        }

        public IScannableItem[] get_selected_path () {
            return (IScannableItem[]) _selected_path.to_array ();
        }

        private void add_to_step_path (IScannableItem item) {
            _step_path.add(item);
            step_item_changed (_step_path.peek_tail ());
        }

        private void add_to_selected_path (IScannableItem item) {
            _selected_path.add(item);
            selected_item_changed (_selected_path.peek_tail ());
        }

        private IScannableItem? get_stepping_child () {
            if (scan_child_index < 0)
                return null;

            return get_scan_children ()[scan_child_index];
        }

        private IScannableItem? get_single_child (IScannableItem item) {
            if (item is ScannableGroup) {
                IScannableItem[] children =
                    (item as ScannableGroup).get_scan_children();
                if (children.length == 1) {
                    return children[0];
                }
            }

            return null;
        }

        public virtual IScannableItem? child_select () {
            IScannableItem step_child = get_stepping_child ();
            IScannableItem selected_leaf = _selected_path.peek_tail ();

            if (selected_leaf != null) {
                assert (selected_leaf is IScannableGroup);
                add_to_selected_path (
                    ((IScannableGroup) selected_leaf).child_select ());
            } else if (step_child != null) {
                step_child.scan_selected = true;
                add_to_selected_path (step_child);
                scan_child_index = -1;

                for (IScannableItem child = get_single_child (step_child);
                     child != null;
                     child = get_single_child (child)) {
                    child.scan_selected = true;
                    add_to_selected_path (child);
                }
            }

            return _selected_path.peek_tail ();
        }

        public void scan_reset () {
            _selected_path.clear ();
            _step_path.clear ();
            scan_child_index = -1;

            foreach (IScannableItem item in get_scan_children ()) {
                item.scan_stepping = false;
                item.scan_selected = false;

                if (item is IScannableGroup)
                    ((IScannableGroup) item).scan_reset ();
            }
            scan_cleared ();
        }

        public IScannableItem? child_step (int cycles) {
            IScannableItem step_child = get_stepping_child ();
            IScannableItem selected_leaf = _selected_path.peek_tail ();

            if (selected_leaf != null) {
                assert (step_child == null);
                if (selected_leaf is IScannableGroup)
                    step_child = ((IScannableGroup) selected_leaf).child_step (
                        cycles);

                if (step_child != null)
                    add_to_step_path (step_child);
                else
                    _step_path.clear ();
            } else if (step_child != null || scan_child_index == -1) {
                assert (selected_leaf == null);
                IScannableItem[] children = get_scan_children ();

                if (scan_child_index == -1)
                    _cycle_count = 0;

                if (scan_child_index == children.length - 1) {
                    scan_child_index = -1;
                    _cycle_count++;
                }

                if (_cycle_count < cycles) {

                    if (step_child != null)
                        step_child.scan_stepping = false;

                    step_child = children[++scan_child_index];
                    step_child.scan_stepping = true;
                    add_to_step_path (step_child);
                } else {
                    _step_path.clear ();
                }
            } else {
                warn_if_reached ();
            }

            return _step_path.peek_tail ();
        }
    }
}