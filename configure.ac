AC_INIT(caribou, 0.1.0, eitan@monotonous.org)
AM_INIT_AUTOMAKE
AM_MAINTAINER_MODE
GNOME_DOC_INIT

dnl == check for python ==
AM_PATH_PYTHON(2.4)

dnl == i18n ==
#GETTEXT_PACKAGE=caribou
#AC_SUBST(GETTEXT_PACKAGE)
#AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [The gettext package])
#AM_GLIB_GNU_GETTEXT

dnl == intltool check ==
#IT_PROG_INTLTOOL([0.35.0])

dnl == generate makefiles ==
AC_OUTPUT([
Makefile
caribou/Makefile
bin/Makefile
bin/caribou
])
