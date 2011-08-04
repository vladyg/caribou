SUBDIRS =

if ENABLE_GTK3_MODULES
SUBDIRS += gtk3
endif

if ENABLE_GTK2_MODULES
SUBDIRS += gtk2
endif

if ENABLE_GTK_MODULES
gtk_modulesdir = $(libdir)/gnome-settings-daemon-3.0/gtk-modules/
gtk_modules_DATA = caribou-gtk-module.desktop
endif

EXTRA_DIST = caribou-gtk-module.desktop
