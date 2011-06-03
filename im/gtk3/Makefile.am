immoduledir = @GTK3_IM_MODULEDIR@
immodule_LTLIBRARIES = im-caribou.la

im_caribou_la_SOURCES = \
	caribou-im.c \
	caribou-imcontext.vala \
	$(NULL)

im_caribou_la_VALAFLAGS = \
	-h caribou-imcontext.h \
	--pkg gtk+-3.0 \
	$(VALAGLAFS)

im_caribou_la_CFLAGS = \
        @GTK3_CFLAGS@ \
        -DG_LOG_DOMAIN=\"CARIBOU\" \
        $(NULL)

im_caribou_la_LIBADD = \
        @GTK3_LIBS@ \
        $(NULL)

im_caribou_la_LDFLAGS = \
        -avoid-version \
        -module \
        $(NULL)

EXTRA_DIST = \
        $(NULL)
