/*
 * Copyright (C) 2011, Eitan Isaacson <eitan@monotonous.org>
 */

#include "caribou-virtual-keyboard.h"
#include "caribou-marshal.h"
#include <X11/Xlib.h>
#include <X11/extensions/XTest.h>
#include <gdk/gdk.h>
#include <gdk/gdkx.h>
#include <X11/XKBlib.h>
#include <libxklavier/xklavier.h>

#define XDISPLAY GDK_DISPLAY_XDISPLAY(gdk_display_get_default ())

struct _CaribouVirtualKeyboardPrivate {
  XkbDescPtr  xkbdesc;
  XklEngine  *xkl_engine;
  gchar modifiers;
  gchar group;
};

G_DEFINE_TYPE (CaribouVirtualKeyboard, caribou_virtual_keyboard, G_TYPE_OBJECT)

enum {
    KB_MODIFIERS_CHANGED,
    KB_GROUP_CHANGED,
	LAST_SIGNAL
};

static guint signals[LAST_SIGNAL] = { 0 };

static void
dispose (GObject *object)
{
  CaribouVirtualKeyboard *self = CARIBOU_VIRTUAL_KEYBOARD (object);

  XkbFreeKeyboard (self->priv->xkbdesc, XkbGBN_AllComponentsMask, True);

  G_OBJECT_CLASS (caribou_virtual_keyboard_parent_class)->dispose (object);
}

static GdkFilterReturn
_filter_x_evt (GdkXEvent *gdk_xevent, GdkEvent *event, gpointer data)
{
  CaribouVirtualKeyboard *self = CARIBOU_VIRTUAL_KEYBOARD (data);
  XkbEvent *xevent = gdk_xevent;

  if (xevent->any.xkb_type == XkbStateNotify) {
    XkbStateNotifyEvent *sevent = &xevent->state;
    if (sevent->changed & XkbGroupStateMask) {
      XklConfigRec *config_rec;
      self->priv->group = sevent->group;
      config_rec = xkl_config_rec_new ();
      xkl_config_rec_get_from_server (config_rec, self->priv->xkl_engine);
      g_signal_emit (self, signals[KB_GROUP_CHANGED], 0,
                     sevent->group,
                     config_rec->layouts[sevent->group],
                     config_rec->variants[sevent->group]);
      g_object_unref (config_rec);
    } else if (sevent->changed & XkbModifierStateMask) {
      self->priv->modifiers = sevent->mods;
      g_signal_emit (self, signals[KB_MODIFIERS_CHANGED], 0, sevent->mods);
    }
  }

  return GDK_FILTER_CONTINUE;
}

static void
caribou_virtual_keyboard_init (CaribouVirtualKeyboard *self)
{
  XkbStateRec sr;

  self->priv = G_TYPE_INSTANCE_GET_PRIVATE ((self), CARIBOU_TYPE_VIRTUAL_KEYBOARD,
                                            CaribouVirtualKeyboardPrivate);

  self->priv->xkbdesc = XkbGetKeyboard(XDISPLAY, XkbGBN_AllComponentsMask,
                                       XkbUseCoreKbd);

  self->priv->xkl_engine = xkl_engine_get_instance (XDISPLAY);

  XkbGetState(XDISPLAY, XkbUseCoreKbd, &sr);

  self->priv->modifiers = sr.mods;
  self->priv->group = sr.group;

  XkbSelectEvents (XDISPLAY,
                   XkbUseCoreKbd, XkbStateNotifyMask | XkbAccessXNotifyMask,
                   XkbStateNotifyMask | XkbAccessXNotifyMask | XkbMapNotifyMask);

  gdk_window_add_filter (NULL, (GdkFilterFunc) _filter_x_evt, self);

}

static void
caribou_virtual_keyboard_class_init (CaribouVirtualKeyboardClass *klass)
{
	GObjectClass *object_class = G_OBJECT_CLASS (klass);

	g_type_class_add_private (klass, sizeof (CaribouVirtualKeyboardPrivate));

	/* virtual method override */
	object_class->dispose = dispose;

	/* signals */

    /**
     * CaribouVirtualKeyboard::modifiers-changed:
     * @virtual_keyboard: the object that received the signal
     * @modifiers: the modifiers that are currently active
     *
     * Emitted when the keyboard modifiers change.
     */
	signals[KB_MODIFIERS_CHANGED] =
      g_signal_new ("modifiers-changed",
                    G_OBJECT_CLASS_TYPE (object_class),
                    G_SIGNAL_RUN_FIRST,
                    0,
                    NULL, NULL,
                    caribou_marshal_NONE__UINT,
                    G_TYPE_NONE, 1, G_TYPE_UINT);

    /**
     * CaribouVirtualKeyboard::group-changed:
     * @virtual_keyboard: the object that received the signal
     * @group: the currently active group
     *
     * Emitted when the keyboard group changes.
     */
	signals[KB_GROUP_CHANGED] =
      g_signal_new ("group-changed",
                    G_OBJECT_CLASS_TYPE (object_class),
                    G_SIGNAL_RUN_FIRST,
                    0,
                    NULL, NULL,
                    caribou_marshal_NONE__UINT_STRING_STRING,
                    G_TYPE_NONE, 3, G_TYPE_UINT, G_TYPE_STRING, G_TYPE_STRING);
}

/**
 * caribou_virtual_keyboard_new:
 *
 * Create a new #CaribouVirtualKeyboard.
 *
 * Returns: A new #CaribouVirtualKeyboard.
 */
CaribouVirtualKeyboard *
caribou_virtual_keyboard_new ()
{
  return g_object_new (CARIBOU_TYPE_VIRTUAL_KEYBOARD, NULL);
}

static KeyCode
keycode_for_keyval (guint                   keyval,
                    guint                  *modmask)
{
  GdkKeymap *km = gdk_keymap_get_default ();
  GdkKeymapKey *kmk;
  gint len;
  KeyCode keycode;

  g_return_val_if_fail (modmask != NULL, 0);

  if (gdk_keymap_get_entries_for_keyval (km, keyval, &kmk, &len)) {
    keycode = kmk[0].keycode;
    *modmask = (kmk[0].level == 1) ? GDK_SHIFT_MASK : 0;
    g_free (kmk);
  }

  return keycode;
}

/**
 * caribou_virtual_keyboard_mod_latch:
 * @mask: the modifier mask
 *
 * Simulate a keyboard modifier key press
 */
void
caribou_virtual_keyboard_mod_latch (CaribouVirtualKeyboard *self,
                                    int                     mask)
{
  XkbLatchModifiers(XDISPLAY, XkbUseCoreKbd, mask, mask);

  gdk_display_sync (gdk_display_get_default ());
}

/**
 * caribou_virtual_keyboard_mod_unlatch:
 * @mask: the modifier mask
 *
 * Simulate a keyboard modifier key release
 */
void
caribou_virtual_keyboard_mod_unlatch (CaribouVirtualKeyboard *self,
                                      int                     mask)
{
  XkbLatchModifiers(XDISPLAY, XkbUseCoreKbd, mask, 0);
  gdk_display_sync (gdk_display_get_default ());
}

/**
 * caribou_virtual_keyboard_keyval_press:
 * @keyval: the keyval to simulate
 *
 * Simulate a keyboard key press with a given keyval.
 */
void
caribou_virtual_keyboard_keyval_press (CaribouVirtualKeyboard *self,
                                       guint                   keyval)
{
  guint mask;
  KeyCode keycode = keycode_for_keyval (keyval, &mask);

  if (mask != 0)
    caribou_virtual_keyboard_mod_latch (self, mask);

  XTestFakeKeyEvent(XDISPLAY, keycode, TRUE, CurrentTime);
  gdk_display_sync (gdk_display_get_default ());
}

/**
 * caribou_virtual_keyboard_keyval_release:
 * @keyval: the keyval to simulate
 *
 * Simulate a keyboard key press with a given keyval.
 */
void
caribou_virtual_keyboard_keyval_release (CaribouVirtualKeyboard *self,
                                         guint                   keyval)
{
  guint mask;
  KeyCode keycode = keycode_for_keyval (keyval, &mask);

  XTestFakeKeyEvent(XDISPLAY, keycode, FALSE, CurrentTime);

  if (mask != 0)
    caribou_virtual_keyboard_mod_unlatch (self, mask);

  gdk_display_sync (gdk_display_get_default ());
}
/**
 * caribou_virtual_keyboard_get_current_group:
 * @group_name: (out) (transfer full): Location to store name of current group,
 *   or NULL.
 * @variant_name: (out) (transfer full): Location to store name of current group's
 *   variant or NULL.
 *
 * Retrieve the keyboard's currently active group.
 *
 * Returns: Current group index.
 */
guint
caribou_virtual_keyboard_get_current_group (CaribouVirtualKeyboard  *self,
                                            gchar                  **group_name,
                                            gchar                  **variant_name)
{
  CaribouVirtualKeyboardPrivate *priv = self->priv;

  if (group_name != NULL || variant_name != NULL) {
    XklConfigRec *config_rec = xkl_config_rec_new ();
    xkl_config_rec_get_from_server (config_rec, priv->xkl_engine);

    if (group_name != NULL)
      *group_name = g_strdup (config_rec->layouts[priv->group]);

    if (variant_name != NULL)
      *variant_name = g_strdup (config_rec->variants[priv->group]);

    g_object_unref (config_rec);
  }

  return priv->group;
}

/**
 * caribou_virtual_keyboard_get_groups:
 * @group_names: (out) (transfer full) (array zero-terminated=1): Location to store
 *   names of available groups or NULL.
 * @variant_names: (out) (transfer full) (array zero-terminated=1): Location to store
 *   variants of available groups or NULL.
 *
 * Retrieve the keyboard's available groups.
 */
void
caribou_virtual_keyboard_get_groups (CaribouVirtualKeyboard   *self,
                                     gchar                  ***group_names,
                                     gchar                  ***variant_names)
{
  CaribouVirtualKeyboardPrivate *priv = self->priv;

  if (group_names != NULL || variant_names != NULL) {
    XklConfigRec *config_rec = xkl_config_rec_new ();
    xkl_config_rec_get_from_server (config_rec, priv->xkl_engine);

    if (group_names != NULL)
      *group_names = g_strdupv (config_rec->layouts);

    if (variant_names != NULL)
      *variant_names = g_strdupv (config_rec->variants);

    g_object_unref (config_rec);
  }
}
