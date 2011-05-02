from caribou.settings.setting_types import *
from caribou.i18n import _

CaribouSettings = SettingsTopGroup(
    _("Caribou Preferences"), "/org/gnome/caribou/", "org.gnome.caribou",
    [SettingsGroup("keyboard", _("Keyboard"), [
                SettingsGroup("general", _("General"), [
                        StringSetting(
                            "keyboard_type", _("Keyboard Type"), "touch",
                            _("The keyboard geometery Caribou should use"),
                            _("The keyboard geometery determines the shape "
                              "and complexity of the keyboard, it could range from "
                              "a 'natural' look and feel good for composing simple "
                              "text, to a fullscale keyboard."),
                            allowed=[(('touch'), _('Touch'))])]),
                ]),
        SettingsGroup("scanning", _("Scanning"), [
                BooleanSetting(
                    "scan_enabled", _("Enable scanning"), False,
                    _("Enable switch scanning"),
                    insensitive_when_false=["scanning_general",
                                            "scanning_input"]),
                SettingsGroup("scanning_general", _("General"), [
                        StringSetting("scanning_type", _("Scanning mode"),
                                      "block",
                                      _("Scanning type, block or row"),
                                      allowed=[("block", _("Block")),
                                                ("row", _("Row"))]),
                        FloatSetting("step_time", _("Step time"), 1.0,
                                     _("Time between key transitions"),
                                     min=0.1, max=60.0),
                        BooleanSetting("reverse_scanning",
                                       _("Reverse scanning"), False,
                                       _("Scan in reverse order"))
                        ]),
                SettingsGroup("scanning_input", _("Input"), [
                        StringSetting("switch_type", _("Switch device"),
                                      "keyboard",
                                      _("Switch device, keyboard or mouse"),
                                      entry_type=ENTRY_RADIO,
                                      allowed=[("keyboard", _("Keyboard")),
                                               ("mouse", _("Mouse"))],
                                      children=[
                                StringSetting("keyboard_key", _("Switch key"),
                                              "Shift_R",
                                              _(
                                        "Key to use with scanning mode"),
                                              allowed=[
                                        ("Shift_R", _("Right shift")),
                                        ("Shift_L", _("Left shift")),
                                        ("ISO_Level3_Shift", _("Alt Gr")),
                                        ("Num_Lock", _("Num lock"))]),
                                StringSetting("mouse_button", _("Switch button"),
                                              "2",
                                              _(
                                        "Mouse button to use in the scanning "
                                        "mode"), 
                                              allowed=[("1", _("Button 1")),
                                                       ("2", _("Button 2")),
                                                       ("3", _("Button 3"))])
                                ]),
                        ]),
                ])
        ])
