fullscalelayoutsdir = $(datadir)/caribou/layouts/fullscale
fullscalelayouts_in_files =\
    us.xml.in
fullscalelayouts_DATA = $(fullscalelayouts_in_files:.xml.in=.xml)

common_files = \
	common/qwerty.xml \
	common/symbols.xml

us.xml: $(common_files)

SUFFIXES = .xml.in .xml

.xml.in.xml:
	$(AM_V_GEN) \
	  rm -f $@ $@.xsl; \
	  xsltproc --xinclude $(top_srcdir)/tools/basic.xsl $@.in > $@.xsl && \
	  xsltproc --xinclude $@.xsl $@.in > $@

EXTRA_DIST = $(fullscalelayouts_in_files) $(common_files)

CLEANFILES = $(fullscalelayouts_DATA) $(fullscalelayouts_in_files:.xml.in=.xml.xsl)

-include $(top_srcdir)/git.mk
