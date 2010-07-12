AC_PREREQ([2.63])
AC_INIT([caribou],
        [0.1.5],
        [https://bugzilla.gnome.org/enter_bug.cgi?product=caribou],
        [caribou])

AC_CONFIG_MACRO_DIR([m4])

AM_INIT_AUTOMAKE([1.11])
AM_MAINTAINER_MODE([enable])
# Support silent build rules. Disable by either passing --disable-silent-rules
# to configure or passing V=1 to make
AM_SILENT_RULES([yes])

dnl == check for python ==
AM_PATH_PYTHON(2.4)

dnl == check for GConf ==
AC_PATH_PROG(GCONFTOOL, gconftool-2)
AM_GCONF_SOURCE_2

dnl == Library dependencies ==
PYGTK_REQUIRED=2.16
PYCLUTTER_REQUIRED=1.0

PKG_CHECK_MODULES(CARIBOU, [
  pygtk-2.0     >= $PYGTK_REQUIRED,
  pyclutter-1.0 >= $PYCLUTTER_REQUIRED])
AC_SUBST(CARIBOU_CFLAGS)
AC_SUBST(CARIBOU_LIBS)

dnl == i18n ==
GETTEXT_PACKAGE=caribou
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [The gettext package])
AM_GLIB_GNU_GETTEXT

dnl == intltool check ==
IT_PROG_INTLTOOL([0.35.0])

dnl == Documentation ==
GNOME_DOC_INIT

dnl == generate makefiles ==
AC_OUTPUT([
Makefile
po/Makefile.in
caribou/Makefile
caribou/common/Makefile
caribou/ui/i18n.py
caribou/ui/Makefile
bin/Makefile
bin/caribou
data/Makefile
data/keyboards/Makefile
])
