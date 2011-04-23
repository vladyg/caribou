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

#define XDISPLAY GDK_DISPLAY_XDISPLAY(gdk_display_get_default ())

struct _CaribouVirtualKeyboardPrivate {
};

G_DEFINE_TYPE (CaribouVirtualKeyboard, caribou_virtual_keyboard, G_TYPE_OBJECT)

enum {
	PLACEHOLDER,
	LAST_SIGNAL
};

static guint signals[LAST_SIGNAL] = { 0 };

static void
dispose (GObject *object)
{
  CaribouVirtualKeyboard *self = CARIBOU_VIRTUAL_KEYBOARD (object);

  G_OBJECT_CLASS (caribou_virtual_keyboard_parent_class)->dispose (object);
}

static void
caribou_virtual_keyboard_init (CaribouVirtualKeyboard *self)
{
  self->priv = G_TYPE_INSTANCE_GET_PRIVATE ((self), CARIBOU_TYPE_VIRTUAL_KEYBOARD,
                                            CaribouVirtualKeyboardPrivate);

}

static void
caribou_virtual_keyboard_class_init (CaribouVirtualKeyboardClass *klass)
{
	GObjectClass *object_class = G_OBJECT_CLASS (klass);

	g_type_class_add_private (klass, sizeof (CaribouVirtualKeyboardPrivate));

	/* virtual method override */
	object_class->dispose = dispose;

	/* signals */
	signals[PLACEHOLDER] =
		g_signal_new ("placeholder",
			      G_OBJECT_CLASS_TYPE (object_class),
			      G_SIGNAL_RUN_FIRST,
			      0,
			      NULL, NULL,
			      caribou_marshal_NONE__NONE,
			      G_TYPE_NONE, 0);
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
