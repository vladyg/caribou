namespace Caribou {
    public interface IScannableItem : Object {
        public abstract bool scan_stepping { get; set; }
        public abstract bool scan_selected { get; set; }
    }
}