#!/usr/bin/python

import xml.dom.minidom

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from caribou.settings import caribou_settings

class SchemasMaker:
    def __init__(self, settings, domain):
        self.settings = settings
        self.domain = domain

    def create_schemas(self, output):
        doc = xml.dom.minidom.Document()
        schemafile =  doc.createElement('schemalist')
        schema = doc.createElement('schema')
        schema.setAttribute("id", self.settings.schema_id)
        schema.setAttribute("gettext-domain", self.domain)
        schemafile.appendChild(schema)
        self._create_schema(self.settings, doc, schema)

        fp = open(output, 'w')
        self._pretty_xml(fp, schemafile)
        fp.close()

    def _attribs(self, e):
        if not list(e.attributes.items()):
            return ""
        return ' ' + ' '.join(['%s="%s"' % (k, v) \
                                   for k, v in list(e.attributes.items())])

    def _pretty_xml(self, fp, e, indent=0):
        if not e.childNodes or \
                (len(e.childNodes) == 1 and \
                     e.firstChild.nodeType == e.TEXT_NODE):
            fp.write('%s%s\n' % (' '*indent*2, e.toxml().strip()))
        else:
            fp.write('%s<%s%s>\n' % (' '*indent*2, e.tagName, self._attribs(e)))
            for c in e.childNodes:
                self._pretty_xml(fp, c, indent + 1)
            fp.write('%s</%s>\n' % (' '*indent*2, e.tagName))

    def _append_children_element_value_pairs(self, doc, element, pairs):
        for e, t in pairs:
            el = doc.createElement(e)
            te = doc.createTextNode(str(t))
            el.appendChild(te)
            element.appendChild(el)

    def _create_schema(self, setting, doc, schemalist):
        if hasattr(setting, 'path'):
            schemalist.setAttribute("path", setting.path)
        if hasattr(setting, 'gsettings_key'):
            key = doc.createElement('key')
            key.setAttribute('name', setting.gsettings_key)
            key.setAttribute('type', setting.variant_type)
            schemalist.appendChild(key)
            # pygobject >= 3.3.3 and up expose g_variant_print as
            # "print_". Older pygobjects expose it as "print", which
            # we need to use through getattr as "print" is a keyword.
            #
            # Try the new name first, fall back to the old one if unavailable.
            #
            # Once we depend on pygobject >= 3.4 we can just call
            # setting.gvariant.print_(False) directly.
            printfunc = getattr(setting.gvariant, 'print_', None)
            if printfunc is None:
                printfunc = getattr(setting.gvariant, 'print')
            self._append_children_element_value_pairs(
                doc, key, [('default', printfunc(False)),
                           ('_summary', setting.short_desc),
                           ('_description', setting.long_desc)])

        for s in setting:
            self._create_schema(s, doc, schemalist)

if __name__ == "__main__":
    from caribou.settings import AllSettings
    from locale import setlocale, LC_ALL
    import argparse

    parser = argparse.ArgumentParser(description='make_schema')

    parser.add_argument('settings_object', type=str,
                        help='Settings object')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='Output file name')
    parser.add_argument('-d', '--domain', type=str, default='caribou',
                        help='Translation domain')

    args = parser.parse_args()

    # prevent _summary and _description from being translated
    setlocale(LC_ALL, "C")

    modulename, settings_obj = args.settings_object.rsplit('.', 1)

    module = __import__(modulename, locals(), globals(), [settings_obj])
    settings = getattr(module, settings_obj)

    maker = SchemasMaker(settings, args.domain)
    maker.create_schemas(args.output)
