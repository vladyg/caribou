distclean_dirs = \
	caribou \
	gtk-doc \
	$(NULL)

docs = \
	caribou-doc \
	caribou-gtk-doc \
	$(NULL)

upload_docs = \
	upload-docs-c-caribou \
	upload-docs-vala-caribou \
	$(NULL)

cariboudocdir=$(datadir)/devhelp/references/caribou
caribouimgdir=$(datadir)/devhelp/references/caribou/img

caribougtkdocdir=$(datadir)/gtk-doc/html/caribou

common_doc_files = \
	*.css \
	*.png \
	*.js \
	index.htm \
	*.html \
	$(NULL)

cariboudoc_DATA = \
	caribou/caribou/caribou.devhelp2 \
	$(addprefix caribou/caribou/,$(common_doc_files)) \
	$(NULL)

caribougtkdoc_DATA = gtk-doc/caribou/html/*

caribouimg_DATA = \
	$(NULL)

$(cariboudoc_DATA) $(caribouimg_DATA): caribou-doc.stamp
$(caribougtkdoc_DATA): caribou-gtk-doc.stamp

valadoc_flags = \
	--force \
	--package-version $(PACKAGE_VERSION) \
	--no-protected \
	$(NULL)

# caribou documentation
caribou_doc_files_blacklist = \
	$(NULL)
# this expands the list of files, so we can filter out elements
caribou_doc_files_all = \
	$(wildcard $(top_srcdir)/libcaribou/*.vala) \
	$(NULL)
# FIXME: sort the files manually to work around the native doclet portion of
# bgo#662784
caribou_doc_files = \
	$(sort \
	$(filter-out $(caribou_doc_files_blacklist),$(caribou_doc_files_all)))
caribou_doc_deps = \
	x11 \
	xtst \
	gdk-3.0 \
	gio-2.0 \
	gee-1.0 \
	libxklavier \
	external-libs \
	gdk-x11-3.0 \
	libxml-2.0 \
	$(NULL)
valadoc_flags_caribou = \
	$(valadoc_flags) \
	-X $(top_srcdir)/libcaribou/caribou.h \
	$(addprefix --pkg=,$(caribou_doc_deps)) \
	--vapidir=$(top_srcdir)/libcaribou \
	$(caribou_doc_files) \
	$(NULL)

caribou-doc.stamp: $(caribou_doc_files)
	$(AM_V_GEN)$(VALADOC) \
		-o caribou/ \
		--doclet=devhelp \
		$(valadoc_flags_caribou) \
		$(NULL)
	@touch $@

caribou-gtk-doc.stamp: $(caribou_doc_files)
	$(AM_V_GEN)$(VALADOC) \
		-X -l -X $(top_builddir)/libcaribou/.libs/libcaribou.so \
		-o gtk-doc/caribou \
		--doclet=gtkdoc \
		$(valadoc_flags_caribou) \
		$(NULL)
	@touch $@

stamps = $(addsuffix .stamp, $(docs))

all: $(stamps)

CLEANFILES = $(stamps)

distclean-local: distclean-docs
distclean-docs:
	rm -rf $(distclean_dirs)

-include $(top_srcdir)/git.mk
