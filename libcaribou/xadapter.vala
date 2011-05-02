using Xkl;
using Gdk;
using Xkb;
using XTest;
using X;

namespace Caribou {
    public class XAdapter : Object {

        /* Signals */
        public signal void modifiers_changed (uint modifiers);
        public signal void group_changed (uint gid, string group, string variant);

        /* Private properties */
        private static XAdapter instance;
        X.Display xdisplay;
        Xkb.Desc xkbdesc;
        Xkl.Engine xkl_engine;
        uint reserved_keysym;
        uchar reserved_keycode;
        uchar modifiers;
        uchar group;

        construct {
            Xkb.State state;

            this.xdisplay = new X.Display ();
            this.xkbdesc = Xkb.get_keyboard (this.xdisplay,
                                             Xkb.GBN_AllComponentsMask,
                                             Xkb.UseCoreKbd);
            this.xkl_engine = Xkl.Engine.get_instance (this.xdisplay);

            Xkb.get_state (this.xdisplay, Xkb.UseCoreKbd, out state);

            this.group = state.group;
            this.modifiers = state.mods;

            this.reserved_keycode = 0;

            Xkb.select_events (
                this.xdisplay, Xkb.UseCoreKbd,
                Xkb.StateNotifyMask | Xkb.AccessXNotifyMask,
                Xkb.StateNotifyMask | Xkb.AccessXNotifyMask);

            ((Gdk.Window) null).add_filter (x_event_filter); // Did I blow your mind?
        }

        ~XAdapter () {
            Xkb.free_keyboard(this.xkbdesc, Xkb.GBN_AllComponentsMask, true);
        }

        public static XAdapter get_default() {
            if (instance == null)
                instance = new XAdapter ();
            return instance;
        }

        private Gdk.FilterReturn x_event_filter (Gdk.XEvent xevent, Gdk.Event event) {
            void* pointer = &xevent;
            Xkb.Event *xev = (Xkb.Event *) pointer;
                        
            if (xev.any.xkb_type == Xkb.StateNotify) {
                Xkb.StateNotifyEvent *sevent = &xev.state;
                if ((sevent.changed & Xkb.GroupStateMask) != 0) {
                    string group_name;
                    string variant_name;
                    this.group = (uchar) sevent.group;
                    get_current_group (out group_name, out variant_name);
                    group_changed (this.group, group_name, variant_name);
                } else if ((sevent.changed & Xkb.ModifierStateMask) != 0) {
                    this.modifiers = (uchar) sevent.mods;
                }
            }

            return Gdk.FilterReturn.CONTINUE;
        }

        private uchar get_reserved_keycode () {
            uchar i;
            unowned Xkb.Desc xkbdesc = this.xkbdesc;

            for (i = xkbdesc.max_key_code; i >= xkbdesc.min_key_code; --i) {
                if (xkbdesc.map.key_sym_map[i].kt_index[0] == Xkb.OneLevelIndex) {
                    if (X.keycode_to_keysym (this.xdisplay, i, 0) != 0) {
                        Gdk.error_trap_push ();
                        this.xdisplay.grab_key (i, 0,
                                    Gdk.x11_get_default_root_xwindow (), true,
                                    X.GrabMode.Sync, X.GrabMode.Sync);
                        this.xdisplay.flush ();
                        this.xdisplay.ungrab_key (
                            i, 0, Gdk.x11_get_default_root_xwindow ());
                        if (Gdk.error_trap_pop () == 0)
                            return i;
                    }
                }
            }

            return (uchar) this.xdisplay.keysym_to_keycode (0x0023); // XK_numbersign
        }

        private void replace_keycode (uint keysym) {
            if (this.reserved_keycode == 0) {
                this.reserved_keycode = get_reserved_keycode ();
                this.reserved_keysym = X.keycode_to_keysym (this.xdisplay,
                                                            this.reserved_keycode, 0);
            }

            this.xdisplay.flush ();
            uint offset = this.xkbdesc.map.key_sym_map[this.reserved_keycode].offset;

            this.xkbdesc.map.syms[offset] = keysym;

            Xkb.set_map (this.xdisplay, Xkb.AllMapComponentsMask, this.xkbdesc);
            /**
             *  FIXME: the use of XkbChangeMap, and the reuse of the priv->xkb_desc
             *  structure, would be far preferable. HOWEVER it does not seem to work
             *  using XFree 4.3.
             **/

            this.xdisplay.flush ();

            if (keysym != this.reserved_keysym)
                GLib.Timeout.add (500, reset_reserved);
        }

        private bool reset_reserved () {
            replace_keycode (this.reserved_keysym);
            return false;
        }

        private uchar keycode_for_keyval (uint keyval, out uint modmask) {
            Gdk.Keymap kmap= Gdk.Keymap.get_default ();
            Gdk.KeymapKey[] kmk;
            uchar keycode = 0;

            if (kmap.get_entries_for_keyval (keyval, out kmk)) {
                Gdk.KeymapKey best_match = kmk[0];
                foreach (KeymapKey km in kmk)
                    if (km.group == this.group)
                        best_match = km;
                
                keycode = (uchar) best_match.keycode;
                modmask = (best_match.level == 1) ? Gdk.ModifierType.SHIFT_MASK : 0;
            } else {
                replace_keycode (keyval);
                keycode = this.reserved_keycode;
            }

            return keycode;
        }

        public void keyval_press (uint keyval) {
            uint mask;
            uchar keycode = keycode_for_keyval (keyval, out mask);

            if (mask != 0)
                mod_latch (mask);

            XTest.fake_key_event (this.xdisplay, keycode, true, X.CURRENT_TIME);
            this.xdisplay.flush ();
        }

        public void keyval_release (uint keyval) {
            uchar keycode = keycode_for_keyval (keyval, null);
            
            XTest.fake_key_event (this.xdisplay, keycode, false, X.CURRENT_TIME);
            this.xdisplay.flush ();
        }

        public void mod_latch (uint mask) {
            Xkb.latch_modifiers (this.xdisplay, Xkb.UseCoreKbd, mask, mask);
            this.xdisplay.flush ();
        }

        public void mod_unlatch (uint mask) {
            Xkb.latch_modifiers (this.xdisplay, Xkb.UseCoreKbd, mask, 0);
            this.xdisplay.flush ();
        }

        public uint get_current_group (out string group_name,
                                       out string variant_name) {
            Xkl.ConfigRec config_rec = new Xkl.ConfigRec ();
            config_rec.get_from_server (this.xkl_engine);
            group_name = config_rec.layouts[this.group];
            variant_name = config_rec.variants[this.group];
            if (variant_name == null)
                variant_name = "";

            return this.group;
        }

        public void get_groups (out string[] group_names,
                                out string[] variant_names) {
            int i;
            Xkl.ConfigRec config_rec = new Xkl.ConfigRec ();
            config_rec.get_from_server (this.xkl_engine);

            for (i=0; i<4; i++)
                if (config_rec.layouts[i] == null) {
                    i--;
                    break;
                }

            group_names = new string[i+1];
            variant_names = new string[i+1];

            for (; i>=0; i--) {
                group_names[i] = config_rec.layouts[i];
                if (config_rec.variants[i] != null)
                    variant_names[i] = config_rec.variants[i];
                else
                    variant_names[i] = "";
            }
        }

        public void me () {
            stdout.printf("%p\n", this.xkl_engine);
        }
    }
}
