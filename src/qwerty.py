# -*- coding: UTF-8 -*-

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
              ( su, "z", "x", "c", "v", "b", "n", "m", ".",  sp,  en) )

uppercase = ( ("?", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"),
              ( np, "A", "S", "D", "F", "G", "H", "J", "K", "L",  bs),
              ( sd, "Z", "X", "C", "V", "B", "N", "M", ".",  sp,  en) )

num_punct = ( ("!", "1", "2", "3", "4", "5", "6",  "7",  "8", "9", "0"),
              ( lt, "@", "$", "/", "+", "-",  up, "\"",  ",", "#",  bs),
              ("'", "(", ")", ";", ":",  le,  dn,   ri,  ".",  sp,  en) )

# the layout that appears in position 0 will be visible
# when the keyboard is first created
layouts = ( "lowercase", "uppercase", "num_punct" )
