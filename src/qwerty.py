# -*- coding: UTF-8 -*-

import keyboardcommon

# TODO add horizontal keysize - will be able to specify a mulitplier
# TODO add key colour
# TODO add noop keysym

# key format ("label", keysym) 
backspace = ("⌫", keyboardcommon.keysyms["backspace"])
# TODO implement numbers and contol caracters
control = (".?12", keyboardcommon.keysyms["space"])

# define keys to switch layers here
# TODO find a better way to specify which layer to switch to
# TODO add ability switch back to previous layer after x keystrokes
shift_up = ("⇧", "layer2")
shift_down = ("⇩", "layer1")

layout1 = ( ("q", "w", "e", "r", "t", "y", "u", "i", "o", "p"),
            ("a", "s", "d", "f", "g", "h", "j", "k", "l", backspace ),
            ("z", "x", "c", "v", "b", "n", "m", " ", control, shift_up) )

layout2 = ( ("Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"),
            ("A", "S", "D", "F", "G", "H", "J", "K", "L", backspace),
            ("Z", "X", "C", "V", "B", "N", "M", " ", control, shift_down) )


keyboard = ( layout1, layout2 )
