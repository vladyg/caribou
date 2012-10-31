bin_SCRIPTS = caribou caribou-preferences
libexec_SCRIPTS = antler-keyboard

DISTCLEANFILES = $(bin_SCRIPTS) $(libexec_SCRIPTS)

all: $(bin_SCRIPTS) $(libexec_SCRIPTS)
	@chmod +x $(bin_SCRIPTS) $(libexec_SCRIPTS)

-include $(top_srcdir)/git.mk
