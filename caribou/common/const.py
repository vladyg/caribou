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

from caribou import data_path

# Application name
APP_NAME = 'Caribou'
APP_SLUG_NAME = 'caribou'

# Paths
DATA_DIR = data_path
KEYBOARDS_DIR = join(DATA_DIR, 'keyboards')

# Preferences
CARIBOU_GCONF = '/apps/caribou/osk'

# Key types
NORMAL_KEY_TYPE = 'normal'
LAYOUT_SWITCHER_KEY_TYPE = 'layout_switcher'
PREFERENCES_KEY_TYPE = 'preferences'
DUMMY_KEY_TYPE = 'dummy'
MASK_KEY_TYPE = 'mask'
