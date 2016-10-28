# 1x1 characters.  Can be displayed directly
# Icons for display (5x8)

# Taken from https://github.com/RandyCupic/RuneAudioLCD/blob/master/display.py

stop		= [ 0b00000, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b00000 ] # Stop
play 		= [ 0b00000, 0b01000, 0b01100, 0b01110, 0b01110, 0b01100, 0b01000, 0b00000 ] # Play
pause 		= [ 0b00000, 0b01010, 0b01010, 0b01010, 0b01010, 0b01010, 0b01010, 0b00000 ] # Pause
ethernet 	= [ 0b00000, 0b11111, 0b11011, 0b10001, 0b10001, 0b10001, 0b11111, 0b00000 ] # Ethernet
wireless	= [ 0b00000, 0b00000, 0b00001, 0b00001, 0b00101, 0b00101, 0b10101, 0b00000 ] # Wireless
note		= [ 0b00000, 0b01111, 0b01001, 0b01001, 0b01001, 0b11011, 0b11011, 0b00000 ] # Music note
power 		= [ 0b00000, 0b00100, 0b00100, 0b10101, 0b10101, 0b10001, 0b01110, 0b00000 ]  # Power

fontpkg = [ stop, play, pause, ethernet, wireless, note, power ]

stop = 0
play = 1
pause = 2
ether = 3
wireless = 4
note = 5
power = 6
