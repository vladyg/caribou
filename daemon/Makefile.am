libexec_PROGRAMS = caribou

caribou_VALAFLAGS = \
	--vapidir=$(top_srcdir)/vapi \
	--pkg config \
	--pkg gdk-x11-3.0 \
	--pkg atspi-2 \
	--pkg posix \
	$(VALAFLAGS)

caribou_CFLAGS = \
	$(CARIBOU_CFLAGS) \
	-DLOCALEDIR=\"$(datadir)/locale\"

caribou_LDADD = \
	$(CARIBOU_LIBS)

caribou_SOURCES = daemon.vala

-include $(top_srcdir)/git.mk
