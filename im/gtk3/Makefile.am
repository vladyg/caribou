immoduledir = @GTK3_IM_MODULEDIR@
immodule_LTLIBRARIES = im-caribou.la

im_caribou_la_SOURCES = \
	caribou-imcontext.vala \
	caribou-im.c \
	$(NULL)

im_caribou_la_VALAFLAGS = \
	-h caribou-imcontext.h \
    --vapidir=. \
	--pkg vapi-fixes \
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
	vapi-fixes.vapi \
	$(NULL)
