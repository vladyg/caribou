tabletlayoutsdir = $(datadir)/caribou/layouts/tablet
tabletlayouts_in_files =\
    bg.xml.in \
    bg+phonetic.xml.in \
    us.xml.in \
    de.xml.in
tabletlayouts_DATA = $(tabletlayouts_in_files:.xml.in=.xml)

common_files = \
	common/qwerty.xml \
	common/qwertz.xml \
	common/symbols.xml \
	common/symbols_ssharp.xml

bg.xml: $(common_files)
bg+phonetic.xml: $(common_files)
us.xml: $(common_files)
de.xml: $(common_files)

SUFFIXES = .xml.in .xml

.xml.in.xml:
	$(AM_V_GEN) \
	  rm -f $@ $@.xsl; \
          srcdir=''; \
            test -f ./$@.in || srcdir=$(srcdir)/; \
	    xsltproc --xinclude $(top_srcdir)/tools/basic.xsl $${srcdir}$@.in > $@.xsl && \
	    xsltproc --xinclude $@.xsl $${srcdir}$@.in > $@

EXTRA_DIST = $(tabletlayouts_in_files) $(common_files)

CLEANFILES = $(tabletlayouts_DATA) $(tabletlayouts_in_files:.xml.in=.xml.xsl)

-include $(top_srcdir)/git.mk
