# -*- coding: UTF-8 -*-

import keyboardcommon

# TODO add horizontal keysize - will be able to specify a mulitplier
# TODO add key colour
# TODO add noop keysym
# TODO add ability switch back to previous layer after x keystrokes
# TODO ensure keyboard doesn't change size when changing layers
# TODO finish numbers and punctuation layout

# key format ("label", keysym) 
bs = ("⌫", keyboardcommon.keysyms["backspace"])
# return
rt = ("rtn", keyboardcommon.keysyms["return"])

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
              ( su, "z", "x", "c", "v", "b", "n", "m", ".", " ",  rt) )

uppercase = ( ("?", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"),
              ( np, "A", "S", "D", "F", "G", "H", "J", "K", "L",  bs),
              ( sd, "Z", "X", "C", "V", "B", "N", "M", ".", " ",  rt) )

num_punct = ( ("!", "1", "2", "3", "4", "5", "6", "7",  "8", "9", "0"),
              ( lt, "@", "$", "/", "+", "-", " ", "\"", ",", ".",  bs),
              ("'", "(", ")", ";", ":", " ", " ", " ",  " ", " ",  rt) )

# the layout that appears in position 0 will be visible
# when the keyboard is first created
layouts = ( "lowercase", "uppercase", "num_punct" )
