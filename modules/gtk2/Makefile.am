gtk_modulesdir = @GTK2_MODULES_DIR@
gtk_modules_LTLIBRARIES = libcaribou-gtk-module.la

libcaribou_gtk_module_la_SOURCES = \
	caribou-gtk-module.vala \
	caribou-module.c \
	$(NULL)

BUILT_SOURCES = caribou-gtk-module.h

libcaribou_gtk_module_la_VALAFLAGS = \
	-h caribou-gtk-module.h \
	--vapidir=. \
	--pkg vapi-fixes \
	--pkg gdk-x11-2.0 \
	--pkg gtk+-2.0 \
	-D GTK2 \
	$(VALAGLAFS)

libcaribou_gtk_module_la_CFLAGS = \
	@GTK2_CFLAGS@ \
	-DG_LOG_DOMAIN=\"CARIBOU\" \
	$(NULL)

libcaribou_gtk_module_la_LIBADD = \
	@GTK2_LIBS@ \
	$(NULL)

libcaribou_gtk_module_la_LDFLAGS = \
	-avoid-version \
	-module \
	$(NULL)

EXTRA_DIST = \
	vapi-fixes.vapi \
	$(NULL)

GITIGNOREFILES = \
        $(libcaribou_gtk_module_la_SOURCES:.vala=.c) \
        libcaribou_gtk_module_la_vala.stamp

-include $(top_srcdir)/git.mk
