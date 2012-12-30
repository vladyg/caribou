namespace Caribou {
    /**
     * Interface implemented by items that can be selected in scanning mode.
     */
    public interface IScannableItem : Object {
        public abstract bool scan_stepping { get; set; }
        public abstract bool scan_selected { get; set; }
    }
}