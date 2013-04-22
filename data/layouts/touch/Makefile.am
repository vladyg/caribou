touchlayoutsdir = $(datadir)/caribou/layouts/touch
touchlayouts_in_files =\
    ara.xml.in \
    il.xml.in \
    us.xml.in
touchlayouts_DATA = $(touchlayouts_in_files:.xml.in=.xml)

common_files = \
	common/qwerty.xml \
	common/symbols.xml

ara.xml: $(common_files)
il.xml: $(common_files)
us.xml: $(common_files)

SUFFIXES = .xml.in .xml

.xml.in.xml:
	$(AM_V_GEN) \
	  rm -f $@ $@.xsl; \
	  xsltproc --xinclude $(top_srcdir)/tools/basic.xsl $@.in > $@.xsl && \
	  xsltproc --xinclude $@.xsl $@.in > $@

EXTRA_DIST = $(touchlayouts_in_files) $(common_files)

CLEANFILES = $(touchlayouts_DATA) $(touchlayouts_in_files:.xml.in=.xml.xsl)

-include $(top_srcdir)/git.mk
