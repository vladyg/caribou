SUBDIRS = keyboards

gtkbuilderdir = $(datadir)/caribou
gtkbuilder_DATA = caribou-prefs.ui
schemadir = $(GCONF_SCHEMA_FILE_DIR)
schema_DATA = caribou.schemas

EXTRA_DIST = $(gtkbuilder_DATA) $(schema_DATA)

# installation of schemas
if GCONF_SCHEMAS_INSTALL
install-data-hook:
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		$(GCONFTOOL) --makefile-install-rule $(srcdir)/$(schema_DATA)
endif