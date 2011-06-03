#include <gtk/gtk.h>
#include <gtk/gtkimmodule.h>
#include "caribou-imcontext.h"

#define CARIBOU_LOCALDIR ""
static const GtkIMContextInfo caribou_im_info = {
    "caribou",
    "Caribou OSK helper module",
    "caribou",
    "",
    "*"
};

static const GtkIMContextInfo *info_list[] = {
    &caribou_im_info
};

G_MODULE_EXPORT const gchar*
g_module_check_init (GModule *module)
{
    return glib_check_version (GLIB_MAJOR_VERSION,
                               GLIB_MINOR_VERSION,
                               0);
}

G_MODULE_EXPORT void
im_module_init (GTypeModule *type_module)
{
    g_type_module_use (type_module);
}

G_MODULE_EXPORT void
im_module_exit (void)
{
}

G_MODULE_EXPORT GtkIMContext *
im_module_create (const gchar *context_id)
{
    if (g_strcmp0 (context_id, "caribou") == 0) {
        CaribouIMContext *context = caribou_im_context_new ();
        return (GtkIMContext *) context;
    }
    return NULL;
}

G_MODULE_EXPORT void
im_module_list (const GtkIMContextInfo ***contexts,
                gint                     *n_contexts)
{
    *contexts = info_list;
    *n_contexts = G_N_ELEMENTS (info_list);
}
