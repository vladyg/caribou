#!/usr/bin/python

from gi.repository import GLib
import xml.dom.minidom

import os,sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from caribou.settings import caribou_settings

class SchemasMaker:
    def __init__(self, settings):
        self.settings = settings

    def create_schemas(self):
        doc = xml.dom.minidom.Document()
        schemafile =  doc.createElement('schemalist')
        schema = doc.createElement('schema')
        schema.setAttribute("id", self.settings.schema_id)
        schemafile.appendChild(schema)
        self._create_schema(self.settings, doc, schema)

        fp = open("%s.gschema.xml.in" % self.settings.schema_id, 'w')
        self._pretty_xml(fp, schemafile)
        fp.close()

    def _attribs(self, e):
        if not e.attributes.items():
            return ""
        return ' ' + ' '.join(['%s="%s"' % (k,v) \
                                   for k,v in e.attributes.items()])

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
            self._append_children_element_value_pairs(
                doc, key, [('default', setting.default_value),
                           ('_summary', setting.short_desc),
                           ('_description', setting.long_desc)])

        for s in setting:
            self._create_schema(s, doc, schemalist)

if __name__ == "__main__":
    from caribou.settings import AllSettings

    if (len(sys.argv) != 2):
        print "usage: %s <schema id>" % sys.argv[0]
        sys.exit(1)

    modulename, settings_obj = sys.argv[-1].rsplit('.', 1)

    module = __import__(modulename, locals(), globals(), [settings_obj])
    settings = getattr(module, settings_obj)

    maker = SchemasMaker(settings)
    maker.create_schemas()
