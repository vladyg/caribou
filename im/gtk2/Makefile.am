immoduledir = @GTK2_IM_MODULEDIR@
immodule_LTLIBRARIES = im-caribou.la

im_caribou_la_SOURCES = \
	caribou-imcontext.vala \
	caribou-im.c \
	$(NULL)

im_caribou_la_VALAFLAGS = \
	-h caribou-imcontext.h \
	--pkg gtk+-2.0 \
	-D GTK2 \
	$(VALAGLAFS)

im_caribou_la_CFLAGS = \
        @GTK2_CFLAGS@ \
        -DG_LOG_DOMAIN=\"CARIBOU\" \
        $(NULL)

im_caribou_la_LIBADD = \
        @GTK2_LIBS@ \
        $(NULL)

im_caribou_la_LDFLAGS = \
        -avoid-version \
        -module \
        $(NULL)

EXTRA_DIST = \
        $(NULL)
