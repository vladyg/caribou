import os
from setting_types import *
from gettext import gettext as _
import caribou.common.const as const
import caribou.ui.i18n
import xml.dom.minidom

GSETTINGS_SCHEMA = "org.gnome.caribou"

try:
    import json
except ImportError:
    HAS_JSON = False
else:
    HAS_JSON = True

def fetch_keyboards():
    try:
        files = os.listdir(const.KEYBOARDS_DIR)
    except:
        files = []
    kbds = []
    for f in files:
        if (HAS_JSON and f.endswith('.json')) or f.endswith('.xml'):
            module = f.rsplit('.', 1)[0]
            # TODO: verify keyboard before adding it to the list
            kbds.append(module)
    return kbds

settings = SettingsGroup("_top", "", [
        SettingsGroup("keyboard", _("Keyboard"), [
                SettingsGroup("general", _("General"), [
                        StringSetting(
                            "layout", _("Keyboard layout"), "qwerty",
                            _("The layout Caribou should use."),
                            _("The layout should be in the data directory of "
                              "Caribou (usually /usr/share/caribou/keyboards) "
                              "and should be a .xml or .json file."),
                            allowed=[(a,a) for a in fetch_keyboards()])]),
                SettingsGroup("color", _("Color"), [
                        BooleanSetting(
                            "default_colors", _("Use system theme"), True,
                            _("Use the default theme colors"),
                            insensitive_when_true=["normal_color",
                                                    "mouse_over_color"]),
                        ColorSetting(
                            "normal_color", _("Normal state"), "grey80",
                            _("Color of the keys when there is no "
                              "event on them")),
                        ColorSetting(
                            "mouse_over_color", _("Mouse over"), "yellow",
                            _("Color of the keys when the mouse goes "
                              "over the key"))]),
                SettingsGroup("fontandsize", _("Font and size"), [
                        BooleanSetting(
                            "default_font", _("Use system fonts"), True,
                            _("Use the default system font for keyboard"),
                            insensitive_when_true=["key_font"]),
                        FontSetting("key_font", _("Key font"), "Sans 12",
                                    _("Custom font for keyboard"))
                        ])
                ]),
        SettingsGroup("scanning", _("Scanning"), [
                BooleanSetting(
                    "scan_enabled", _("Enable scanning"), False,
                    _("Enable switch scanning"),
                    insensitive_when_false=["scanning_general",
                                            "scanning_input",
                                            "scanning_color"]),
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
                SettingsGroup("scanning_color", _("Color"), [
                        ColorSetting("block_scanning_color", _("Block color"),
                                     "purple", _("Color of block scans")),
                        ColorSetting("row_scanning_color", _("Row color"),
                                     "green", _("Color of row scans")),
                        ColorSetting("button_scanning_color", _("Key color"),
                                      "cyan", _("Color of key scans")),
                        ColorSetting("cancel_scanning_color",
                                     _("Cancel color"),
                                     "red", _("Color of cancel scan"))
                        ])
                ])
        ])

if __name__ == "__main__":
    from gi.repository import GLib

    class SchemasMaker:
        def create_schemas(self):
            doc = xml.dom.minidom.Document()
            schemafile =  doc.createElement('schemalist')
            schema = doc.createElement('schema')
            schema.setAttribute("id", GSETTINGS_SCHEMA)
            schema.setAttribute("path", "/org/gnome/caribou/osk/")
            schemafile.appendChild(schema)
            self._create_schema(settings, doc, schema)

            self._pretty_xml(schemafile)

        def _attribs(self, e):
            if not e.attributes.items():
                return ""
            return ' ' + ' '.join(['%s="%s"' % (k,v) \
                                       for k,v in e.attributes.items()])

        def _pretty_xml(self, e, indent=0):
            if not e.childNodes or \
                    (len(e.childNodes) == 1 and \
                         e.firstChild.nodeType == e.TEXT_NODE):
                print '%s%s' % (' '*indent*2, e.toxml().strip())
            else:
                print '%s<%s%s>' % (' '*indent*2, e.tagName, self._attribs(e))
                for c in e.childNodes:
                    self._pretty_xml(c, indent + 1)
                print '%s</%s>' % (' '*indent*2, e.tagName)

        def _append_children_element_value_pairs(self, doc, element, pairs):
            for e, t in pairs:
                el = doc.createElement(e)
                te = doc.createTextNode(str(t))
                el.appendChild(te)
                element.appendChild(el)

        def _create_schema(self, setting, doc, schemalist):
            if hasattr(setting, 'gsettings_key'):
                key = doc.createElement('key')
                key.setAttribute('name', setting.gsettings_key)
                key.setAttribute('type', setting.variant_type)
                schemalist.appendChild(key)
                self._append_children_element_value_pairs(
                    doc, key, [('default',
                                getattr(setting.gvariant, "print")(False)),
                               ('_summary', setting.short_desc),
                               ('_description', setting.long_desc)])

            for s in setting:
                self._create_schema(s, doc, schemalist)

    maker = SchemasMaker()
    maker.create_schemas()
