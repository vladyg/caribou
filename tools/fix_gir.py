#!/usr/bin/python

from xml.dom import minidom

def purge_white_space_and_fix_namespace(node, indent=0):
    if getattr(node, "tagName", None) == "namespace":
        name = node.getAttribute("name")
        node.setAttribute("name", name.lstrip('_'))
    for child in [c for c in node.childNodes]:
        if child.nodeType == node.TEXT_NODE or \
                getattr(child, "tagName", None) == "annotation":
            node.removeChild(child)
            continue
        purge_white_space_and_fix_namespace(child, indent+1)

def find_ancestor(node, name):
    if getattr(node, "tagName", None) == name:
        return node
    parent = getattr(node, "parentNode", None)
    if not parent:
        return None
    return find_ancestor(parent, name)

def fix_vfuncs(dom):
    for f in dom.getElementsByTagName("callback"):
        record = find_ancestor(f, "record")
        if not record:
            continue

        name = record.getAttribute("name")
        cname = record.getAttribute("c:type")

        assert(name.endswith("Class") or name.endswith("Iface"))
        assert(cname.endswith("Class") or name.endswith("Iface"))

        params = (f.getElementsByTagName("parameters") or [None])[0]

        if not params:
            params = dom.createElement("parameters")
            f.insertBefore(params, f.firstChild)

        param = dom.createElement("parameter")
        param.setAttribute("name", "self")
        param.setAttribute("transfer-ownership", "none")
        ptype = dom.createElement("type")
        ptype.setAttribute("name", name[:-5])
        ptype.setAttribute("c:type", cname[:-5])
        param.appendChild(ptype)
        params.insertBefore(param, params.firstChild)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print "supply a gir file"
        sys.exit(1)

    dom = minidom.parse(sys.argv[-1])

    purge_white_space_and_fix_namespace(dom)
    fix_vfuncs(dom)

    print dom.toprettyxml(indent=" ", newl="\n")
