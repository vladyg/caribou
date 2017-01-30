touchlayoutsdir = $(datadir)/caribou/layouts/touch
touchlayouts_in_files =\
    ara.xml.in \
    cs.xml.in \
    de.xml.in \
    fr.xml.in \
    il.xml.in \
    ru.xml.in \
    us.xml.in
touchlayouts_DATA = $(touchlayouts_in_files:.xml.in=.xml)

common_files = \
	common/azerty.xml \
	common/qwerty.xml \
	common/qwertz.xml \
	common/symbols.xml

ara.xml: $(common_files)
cs.xml: $(common_files)
de.xml: $(common_files)
il.xml: $(common_files)
ru.xml: $(common_files)
us.xml: $(common_files)

SUFFIXES = .xml.in .xml

.xml.in.xml:
	$(AM_V_GEN) \
	  rm -f $@ $@.xsl; \
          srcdir=''; \
            test -f ./$@.in || srcdir=$(srcdir)/; \
	    xsltproc --xinclude $(top_srcdir)/tools/basic.xsl $${srcdir}$@.in > $@.xsl && \
	    xsltproc --xinclude $@.xsl $${srcdir}$@.in > $@

EXTRA_DIST = $(touchlayouts_in_files) $(common_files)

CLEANFILES = $(touchlayouts_DATA) $(touchlayouts_in_files:.xml.in=.xml.xsl)

-include $(top_srcdir)/git.mk
