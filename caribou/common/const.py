# -*- coding: utf-8 -*-
#
# Caribou - text entry and UI navigation application
#
# Copyright (C) 2010 Warp Networks S.L.
#  * Contributor: David Pellicer <dpellicer@warp.es>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from os.path import join
from os.path import dirname

import gtk

# Application name
APP_NAME = 'Caribou'
APP_SLUG_NAME = 'caribou'

# Paths
DATA_DIR = join('/usr', 'share', '%s' % APP_SLUG_NAME)
RESOURCES_DIR = join(DATA_DIR, 'resources')
KEYBOARDS_DIR = join(RESOURCES_DIR, 'keyboards')
CONFIG_DIR = join(RESOURCES_DIR, 'config')
DATABASES_DIR = join(RESOURCES_DIR, 'databases')
GLADE_UIS_DIR = join(RESOURCES_DIR, 'uis')

# Preferences
CARIBOU_GCONF = join('/apps', 'caribou', 'osk')

# Key types
NORMAL_KEY_TYPE = 'normal'
LAYOUT_SWITCHER_KEY_TYPE = 'layout_switcher'
PREFERENCES_KEY_TYPE = 'preferences'
DUMMY_KEY_TYPE = 'dummy'
MASK_KEY_TYPE = 'mask'

KEY_MASKS = {'shift': gtk.gdk.SHIFT_MASK,
             'lock': gtk.gdk.LOCK_MASK,
             'control': gtk.gdk.CONTROL_MASK,
             'mod1': gtk.gdk.MOD1_MASK,
             'mod2': gtk.gdk.MOD2_MASK,
             'mod3': gtk.gdk.MOD3_MASK,
             'mod4': gtk.gdk.MOD4_MASK,
             'mod5': gtk.gdk.MOD5_MASK,
             'button1': gtk.gdk.BUTTON1_MASK,
             'button2': gtk.gdk.BUTTON2_MASK,
             'button3': gtk.gdk.BUTTON3_MASK,
             'button4': gtk.gdk.BUTTON4_MASK,
             'button5': gtk.gdk.BUTTON5_MASK}
