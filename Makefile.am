ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}

SUBDIRS = caribou bin data po libcaribou modules tools vapi

if HAVE_VALADOC
SUBDIRS += docs
endif

DISTCHECK_CONFIGURE_FLAGS = \
	--enable-docs \
	$(NULL)

GITIGNOREFILES = \
        INSTALL \
	aclocal.m4 \
	config.guess \
	config.sub \
	depcomp \
	git.mk \
	install-sh \
	ltmain.sh \
	m4 \
	missing \
	mkinstalldirs \
	py-compile

-include $(top_srcdir)/git.mk
