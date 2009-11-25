# -*- coding: UTF-8 -*-
#
# Carbou - On-screen Keyboard and UI navigation application
#
# Copyright (C) 2009 Adaptive Technology Resource Centre
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

import keysyms 

# TODO add horizontal keysize - will be able to specify a mulitplier
# TODO add key colour
# TODO add noop keysym
# TODO add ability switch back to previous layer after x keystrokes
# TODO ensure keyboard doesn't change size when changing layers
# TODO finish numbers and punctuation layout

# key format ("label", keysym) 
bs = ("⌫", keysyms.backspace)
# enter 
en = ("↲", keysyms.enter)
# space
sp = ("␣", keysyms.space)
# up
up = ("↑", keysyms.up)
# down
dn = ("↓", keysyms.down)
# left
le = ("←", keysyms.left)
# right
ri = ("→", keysyms.right)


# define keys to switch layers here
# shift up
su = ("⇧", "uppercase")
# shift down
sd = ("⇩", "lowercase")
# number and punctuation
np = (".?12", "num_punct") 
# letters
lt = ("abc", "lowercase")


# keyboard layouts - put a single utf-8 character or a tuple defined above
lowercase = ( ("?", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p"),
              ( np, "a", "s", "d", "f", "g", "h", "j", "k", "l",  bs),
              ( su, "z", "x", "c", "v", "b", "n", "m", sp,  ".",  en) )

uppercase = ( ("?", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"),
              ( np, "A", "S", "D", "F", "G", "H", "J", "K", "L",  bs),
              ( sd, "Z", "X", "C", "V", "B", "N", "M",  sp, ".",  en) )

num_punct = ( ("!", "1", "2", "3", "4", "5", "6",  "7",  "8", "9", "0"),
              ( lt, "@", "$", "/", "+", "-",  up, "\"",  ",", "#",  bs),
              ("'", "(", ")", ";", ":",  le,  dn,   ri,   sp, ".",  en) )

# the layout that appears in position 0 will be visible
# when the keyboard is first created
layouts = ( "lowercase", "uppercase", "num_punct" )
