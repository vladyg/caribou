SUBDIRS = keyboards

@GSETTINGS_RULES@
@INTLTOOL_XML_NOMERGE_RULE@
gsettings_schemas_in_files = org.gnome.caribou.gschema.xml.in
gsettings_SCHEMAS = $(gsettings_schemas_in_files:.gschema.xml.in=.gschema.xml)

desktopdir = $(datadir)/applications
desktop_in_files = caribou.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)

autostartdir	 = $(sysconfdir)/xdg/autostart
autostart_in_files = caribou-autostart.desktop.in
autostart_DATA   = $(autostart_in_files:.desktop.in=.desktop)

@INTLTOOL_DESKTOP_RULE@

EXTRA_DIST = $(desktop_in_files) $(autostart_in_files)

org.gnome.caribou.gschema.xml.in: $(top_srcdir)/caribou/common/settings.py
	PYTHONPATH=${PYTHONPATH}:$(top_srcdir) $(PYTHON) $< > $@

CLEANFILES = $(desktop_DATA) \
	$(autostart_DATA) \
	$(gsettings_schemas_in_files) \
	$(gsettings_SCHEMAS)
