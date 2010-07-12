SUBDIRS = keyboards

gtkbuilderdir = $(datadir)/caribou
gtkbuilder_DATA = caribou-prefs.ui

schemadir = $(GCONF_SCHEMA_FILE_DIR)
schema_DATA = caribou.schemas

desktopdir = $(datadir)/applications
desktop_in_files = caribou.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

EXTRA_DIST = $(gtkbuilder_DATA) \
             $(schema_DATA) \
             $(desktop_in_files)

CLEANFILES = $(desktop_DATA)
# installation of schemas
if GCONF_SCHEMAS_INSTALL
install-data-hook:
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		$(GCONFTOOL) --makefile-install-rule $(srcdir)/$(schema_DATA)

uninstall-hook:
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		$(GCONFTOOL) --makefile-uninstall-rule $(srcdir)/$(schema_DATA)
endif
