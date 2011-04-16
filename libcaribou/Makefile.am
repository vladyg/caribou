INCLUDES =                              \
        -DG_LOG_DOMAIN=\"libcaribou\"   \
        -I$(top_srcdir)                 \
        $(LIBCARIBOU_CFLAGS)


MARSHAL_GENERATED = caribou-marshal.c caribou-marshal.h
MKENUMS_GENERATED = caribou-enum-types.c caribou-enum-types.h

caribou-marshal.h: caribou-marshal.list
	$(AM_V_GEN) ( $(GLIB_GENMARSHAL) --prefix=caribou_marshal $(srcdir)/caribou-marshal.list --header > caribou-marshal.tmp \
	&& mv caribou-marshal.tmp caribou-marshal.h ) \
	|| ( rm -f caribou-marshal.tmp && exit 1 )

caribou-marshal.c: caribou-marshal.h
	$(AM_V_GEN) ( (echo '#include "caribou-marshal.h"'; $(GLIB_GENMARSHAL) --prefix=caribou_marshal $(srcdir)/caribou-marshal.list --body) > caribou-marshal.tmp \
	&& mv caribou-marshal.tmp caribou-marshal.c ) \
	|| ( rm -f caribou-marshal.tmp && exit 1 )

caribou-enum-types.h: $(caribou_headers)
	$(AM_V_GEN) ( cd $(srcdir) && $(GLIB_MKENUMS) --template caribou-enum-types.h.tmpl \
		$(caribou_headers) ) > caribou-enum-types.h.tmp \
	&& mv caribou-enum-types.h.tmp caribou-enum-types.h \
	|| rm -f caribou-enum-type.h.tmp

caribou-enum-types.c: $(libcaribouinclude_HEADERS)
	$(AM_V_GEN) ( cd $(srcdir) && $(GLIB_MKENUMS) --template caribou-enum-types.c.tmpl \
		$(caribou_headers) ) > caribou-enum-types.c.tmp \
	&& mv caribou-enum-types.c.tmp caribou-enum-types.c \
	|| rm -f caribou-enum-type.c.tmp

BUILT_SOURCES = $(MARSHAL_GENERATED) $(MKENUMS_GENERATED)

CLEANFILES = $(MARSHAL_GENERATED) $(MKENUMS_GENERATED)

libcaribouincludedir = $(includedir)/libcaribou

caribou_headers =		  \
	caribou.h		      \
	caribou-virtual-keyboard.h

libcaribouinclude_HEADERS =	\
	$(caribou_headers)	 \
	caribou-enum-types.h

lib_LTLIBRARIES = libcaribou.la

libcaribou_la_LIBADD = \
	$(LIBCARIBOU_LIBS)

libcaribou_la_SOURCES =		\
	$(BUILT_SOURCES)	    \
	caribou-virtual-keyboard.c

#
# Introspection support
#
include $(INTROSPECTION_MAKEFILE)
INTROSPECTION_GIRS =
INTROSPECTION_SCANNER_ARGS = --add-include-path=.
INTROSPECTION_COMPILER_ARGS = --includedir=.

if HAVE_INTROSPECTION

gi_caribou_files = \
	$(filter-out caribou.h caribou-enum-types.% caribou-marshal.h,\
	   $(caribou_headers) $(filter-out %.h, $(libcaribou_la_SOURCES)))
# gi_built_caribou_files = caribou-enum-types.h

Caribou-1.0.gir: libcaribou.la
Caribou_1_0_gir_INCLUDES = Gdk-3.0
Caribou_1_0_gir_CFLAGS = $(INCLUDES)
Caribou_1_0_gir_LIBS = libcaribou.la
Caribou_1_0_gir_EXPORT_PACKAGES = libcaribou
Caribou_1_0_gir_SCANNERFLAGS = --c-include "libcaribou/caribou.h"
Caribou_1_0_gir_FILES = \
	$(addprefix $(srcdir)/, $(gi_caribou_files)) \
	$(foreach f,$(gi_built_caribou_files), \
	   $(if $(shell test -f $(addprefix $(srcdir)/,$(f)) && echo yes), \
	      $(addprefix $(srcdir)/,$(f)), \
	      $(f)))

INTROSPECTION_GIRS += Caribou-1.0.gir

girdir = $(datadir)/gir-1.0
gir_DATA = $(INTROSPECTION_GIRS)

typelibsdir = $(libdir)/girepository-1.0
typelibs_DATA = $(INTROSPECTION_GIRS:.gir=.typelib)

CLEANFILES += $(gir_DATA) $(typelibs_DATA)

endif