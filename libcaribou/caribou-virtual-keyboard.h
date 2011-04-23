/*
 * Copyright (C) 2011, Eitan Isaacson <eitan@monotonous.org>
 */

#ifndef CARIBOU_VIRTUAL_KEYBOARD_H
#define CARIBOU_VIRTUAL_KEYBOARD_H

#include <glib-object.h>

G_BEGIN_DECLS

#define CARIBOU_TYPE_VIRTUAL_KEYBOARD            (caribou_virtual_keyboard_get_type ())
#define CARIBOU_VIRTUAL_KEYBOARD(obj)            (G_TYPE_CHECK_INSTANCE_CAST ((obj), CARIBOU_TYPE_VIRTUAL_KEYBOARD, CaribouVirtualKeyboard))
#define CARIBOU_VIRTUAL_KEYBOARD_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST ((klass), CARIBOU_TYPE_VIRTUAL_KEYBOARD, CaribouVirtualKeyboardClass))
#define CARIBOU_IS_VIRTUAL_KEYBOARD(obj)         (G_TYPE_CHECK_INSTANCE_TYPE ((obj), CARIBOU_TYPE_VIRTUAL_KEYBOARD))
#define CARIBOU_IS_VIRTUAL_KEYBOARD_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE ((obj), CARIBOU_TYPE_VIRTUAL_KEYBOARD))
#define CARIBOU_VIRTUAL_KEYBOARD_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS ((obj), CARIBOU_TYPE_VIRTUAL_KEYBOARD, CaribouVirtualKeyboardClass))

typedef struct _CaribouVirtualKeyboard CaribouVirtualKeyboard;
typedef struct _CaribouVirtualKeyboardClass CaribouVirtualKeyboardClass;
typedef struct _CaribouVirtualKeyboardPrivate CaribouVirtualKeyboardPrivate;

struct _CaribouVirtualKeyboard {
  GObject parent;

  CaribouVirtualKeyboardPrivate *priv;
};

struct _CaribouVirtualKeyboardClass {
  GObjectClass parent_class;

};

GType caribou_virtual_keyboard_get_type (void);

CaribouVirtualKeyboard *caribou_virtual_keyboard_new ();

void caribou_virtual_keyboard_keyval_press (CaribouVirtualKeyboard *self,
                                            guint                   keyval);

void caribou_virtual_keyboard_keyval_release (CaribouVirtualKeyboard *self,
                                              guint                   keyval);

void caribou_virtual_keyboard_mod_latch (CaribouVirtualKeyboard *self,
                                         int                     mask);

void caribou_virtual_keyboard_mod_unlatch (CaribouVirtualKeyboard *self,
                                           int                     mask);

guint caribou_virtual_keyboard_get_current_group (CaribouVirtualKeyboard  *self,
                                                  gchar                  **group_name,
                                                  gchar                  **variant_name);

void caribou_virtual_keyboard_get_groups (CaribouVirtualKeyboard   *self,
                                          gchar                  ***group_names,
                                          gchar                  ***variant_names);
G_END_DECLS

#endif /* CARIBOU_VIRTUAL_KEYBOARD_H */
