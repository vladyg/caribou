lib_LTLIBRARIES = libcaribou.la

INCLUDES = \
	-DG_LOG_DOMAIN=\"caribou\" \
	-I$(top_srcdir) \
	$(LIBCARIBOU_CFLAGS)

libcaribou_la_VALAFLAGS = \
	-H caribou.h --vapi caribou-1.0.vapi \
	-h caribou-internals.h \
	--vapidir=. \
	--pkg x11 --pkg libxklavier --pkg external-libs --pkg gdk-3.0 --pkg gdk-x11-3.0 \
	--internal-vapi caribou-internals-1.0.vapi \
	--library caribou-1.0 --gir Caribou-1.0.gir \
	$(VALAFLAGS)

libcaribou_la_CPPFLAGS = \
	$(INCLUDES)

libcaribouincludedir = $(includedir)/libcaribou

caribouinclude_headers = \
	caribou.h

libcaribouinclude_HEADERS = \
	$(caribou_headers)

libcaribou_la_LIBADD = \
	$(LIBCARIBOU_LIBS)

libcaribou_la_SOURCES = \
	xadapter.vala

EXTRA_DIST = \
	external-libs.vapi \
	libxklavier.vapi

#
# Introspection support
#

if HAVE_INTROSPECTION
girdir = $(datadir)/gir-1.0
gir_DATA = Caribou-1.0.gir

typelibdir = $(libdir)/girepository-1.0
typelib_DATA = Caribou-1.0.typelib

Caribou-1.0.typelib: Caribou-1.0.gir
	@INTROSPECTION_COMPILER@ --shared-library=libcaribou -o $@ $^
endif

Caribou-1.0.gir caribou-internals-1.0.vapi caribou-1.0.vapi: libcaribou.la

CLEANFILES = \
	caribou-1.0.vapi \
	caribou-internals-1.0.vapi \
	Caribou-1.0.typelib \
	Caribou-1.0.gir \
	*.[ch]