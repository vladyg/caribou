SUBDIRS = keyboards

schemasdir = $(GCONF_SCHEMA_FILE_DIR)
schemas_in_files = caribou.schemas.in
schemas_DATA = $(schemas_in_files:.schemas.in=.schemas)
@INTLTOOL_SCHEMAS_RULE@

desktopdir = $(datadir)/applications
desktop_in_files = caribou.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

EXTRA_DIST = $(desktop_in_files)

caribou.schemas.in: $(top_srcdir)/caribou/common/settings.py
	PYTHONPATH=$(top_srcdir) $(PYTHON) $< > $@

CLEANFILES = $(desktop_DATA) \
	$(schemas_in_files) \
	$(schemas_DATA)

# installation of schemas
if GCONF_SCHEMAS_INSTALL
install-data-hook:
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		$(GCONFTOOL) --makefile-install-rule $(schemas_DATA)

uninstall-hook:
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		$(GCONFTOOL) --makefile-uninstall-rule $(schemas_DATA)
endif
