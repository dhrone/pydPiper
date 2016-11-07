# Icons for large number display (for large clock over 2 lines)

ful	= [ 0b00111, 0b01111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111 ] # Block with upper left rounded
fll	= [ 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b01111, 0b00111 ] # Block with lower left rounded
fur	= [ 0b11100, 0b11110, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111 ] # Block with upper right rounded
flr	= [ 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11110, 0b11100 ] # Block with lower right rounded
fub	= [ 0b11111, 0b11111, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000 ] # Upper bar
flb	= [ 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111 ] # Lower bar
fuln= [ 0b11111, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111 ] # Upper lower thin
fulk =[ 0b11111, 0b11111, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111 ] # Upper lower thick


fontpkg = [ ful, fll, fur, flr, fub, flb, fuln , fulk ]

ul = 0
ll = 1
ur = 2
lr = 3
ub = 4
lb = 5
uln = 6
ulk = 7

emp = 32 # Empty block

# Numeric patterns 3x2

one     = [ [emp,  ur, emp], [ lb,  lr,  lb] ]
two     = [ [ulk, ulk,  ur], [ ll, uln, uln] ]
three   = [ [ulk, ulk,  ur], [uln, uln,  lr] ]
four    = [ [ lr,  lb,  ur], [emp, emp,  lr] ]
five    = [ [ ul, ulk, ulk], [uln, uln,  lr] ]
six     = [ [ ul, ulk, ulk], [ lr, uln,  lr] ]
seven   = [ [ ub,  ub,  ur], [emp,  ur, emp] ]
eight   = [ [ ul, ulk,  ur], [ ll, uln,  lr] ]
nine    = [ [ ll, ulk,  ur], [emp, emp,  lr] ]
zero    = [ [ ul, ub,   ur], [ ll,  lb,  lr] ]

numbers = [ zero, one, two, three, four, five, six, seven, eight, nine ]
