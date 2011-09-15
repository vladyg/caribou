#include <gtk/gtk.h>
#include "caribou-gtk-module.h"

CaribouGtkModule * gtk_module;

G_MODULE_EXPORT CaribouGtkModule *
gtk_module_init (gint *argc, gchar ***argv[]) {
    CaribouGtkModule *context = caribou_gtk_module_new ();
    gtk_module = context;
        return context;
}

G_MODULE_EXPORT const gchar*
g_module_check_init (GModule *module)
{
    const gchar *error;

    error = gtk_check_version (GTK_MAJOR_VERSION, 0, 0);
    if (error)
        return error;

    g_module_make_resident (module);
    return NULL;
}
