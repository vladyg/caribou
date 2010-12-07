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
from caribou import data_path

# Application name
APP_NAME = 'Caribou'
APP_SLUG_NAME = 'caribou'

# Paths
DATA_DIR = data_path
KEYBOARDS_DIR = join(DATA_DIR, 'keyboards')

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

# Scan constans
BUTTON = 'button'
ROW = '1'
BLOCK = '0'
CANCEL = 'cancel'
REVERSE = 'reverse'
MOUSE_SWITCH_TYPE = 'mouse'
KEYBOARD_SWITCH_TYPE = 'keyboard'
KEYBOARD_KEY_LIST = {"Shift R" : "Shift_R",
                     "Shift L" : "Shift_L", 
                     "Alt Gr"  : "ISO_Level3_Shift",
                     "Num Lock": "Num_Lock"}
DEFAULT_KEYBOARD_KEY = 'Shift R'
DEFAULT_MOUSE_BUTTON = '1'
MIN_STEP_TIME = 50
MAX_STEP_TIME = 5000
TIME_SINGLE_INCREMENT = 1
TIME_MULTI_INCREMENT = 10
DEFAULT_STEP_TIME = 1000
DEFAULT_SCANNING_TYPE = ROW
DEFAULT_SWITCH_TYPE = KEYBOARD_SWITCH_TYPE
