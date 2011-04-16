AC_PREREQ([2.63])
AC_INIT([caribou],
        [0.2.00],
        [https://bugzilla.gnome.org/enter_bug.cgi?product=caribou],
        [caribou])

AC_CONFIG_MACRO_DIR([m4])

AM_PROG_LIBTOOL

AM_INIT_AUTOMAKE([1.11])
AM_MAINTAINER_MODE([enable])
# Support silent build rules. Disable by either passing --disable-silent-rules
# to configure or passing V=1 to make
AM_SILENT_RULES([yes])


AM_PATH_GLIB_2_0(2.27.5,,,gobject)
if test "$GLIB_LIBS" = ""; then
   AC_MSG_ERROR(GLIB 2.27.5 or later is required to build libcaribou)
fi

dnl == check for python ==
AM_PATH_PYTHON(2.4)

dnl == Library dependencies ==
PYGOBJECT_REQUIRED=2.27.92
GTK_REQUIRED=3.0.0
CLUTTER_REQUIRED=1.5.11
GDK_REQUIRED=3.0.0

PKG_CHECK_MODULES(CARIBOU, [
  pygobject-2.0 >= $PYGOBJECT_REQUIRED,
  gtk+-3.0      >= $GTK_REQUIRED,
  clutter-1.0   >= $CLUTTER_REQUIRED
  ])
AC_SUBST(CARIBOU_CFLAGS)
AC_SUBST(CARIBOU_LIBS)

PKG_CHECK_MODULES(LIBCARIBOU, [
  gdk-3.0 >= $GDK_REQUIRED,
  xtst,
  x11
  ])
AC_SUBST(LIBCARIBOU_CFLAGS)
AC_SUBST(LIBCARIBOU_LIBS)

dnl == i18n ==
GETTEXT_PACKAGE=caribou
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [The gettext package])
AM_GLIB_GNU_GETTEXT

GLIB_GSETTINGS

dnl == intltool check ==
IT_PROG_INTLTOOL([0.35.0])

dnl == Documentation ==
GNOME_DOC_INIT

dnl == GObject introspection ==
GOBJECT_INTROSPECTION_CHECK([0.10.7])

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
libcaribou/Makefile
])
