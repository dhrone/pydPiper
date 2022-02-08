#!/usr/bin/python
# coding: UTF-8
from time import sleep
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

PINS = [ 25, 24, 23, 27]
RS = 7
E = 8
for pin in PINS:
   GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

GPIO.setup(E, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(RS, GPIO.OUT, initial=GPIO.LOW)

imode = False

class ws0010(object):
    CLEAR = 0x01
    HOME = 0x02
    ENTRY = 0x06
    DISPLAYOFF = 0x08
    DISPLAYON = 0x0C
    POWEROFF = 0x13
    POWERON = 0x17
    GRAPHIC = 0x08
    CHAR = 0x00
    FUNCTIONSET = 0x29
    DL8 = 0x10
    DL4 = 0x00
    DDRAMADDR = 0x80
    CGRAMADDR = 0x40


_cmd_mode = GPIO.LOW
_data_mode = GPIO.HIGH

def command(*cmd):
    """
    Sends a command or sequence of commands through the bus

    :param cmd: A spread of commands.
    :type cmd: int
    """
    _write_bytes(list(cmd), _cmd_mode)

def data(data):
    """
    Sends a data byte or sequence of data bytes through to the bus.
    If the bus is in four bit mode, each byte is sent as two 4 bit values.

    :param data: A data sequence.
    :type data: list, bytearray
    """
    _write_bytes(data, _data_mode)

def _write_bytes(data, mode):
    gpio = GPIO
    gpio.output(RS, mode)
    gpio.output(E, gpio.LOW)  # Active low
    for byte in data:
        if imode:
            _write(byte, 8)
        else:
            _write(byte>>4, 4)
            _write(byte, 4)
        if mode == _cmd_mode:
            sleep(1e-6*40)


def _write(value, bits):
    assert bits in (4,8)
    gpio = GPIO
    gpio.output(E, gpio.LOW)
    for i in range(bits):
        gpio.output(PINS[i], (value >> i) & 0x01)
    gpio.output(E, gpio.HIGH)
    sleep(1e-7) # Minimum time for enable is ~1/2 uS
    gpio.output(E, gpio.LOW)


def _reset():
    c = ws0010
    mode = c.DL4
    command(0x00, 0x00, 0x02, 0x29) # Sends five 0s followed a two to set into 4 bit mode and FUNCTIONSET (e.g. 0x29 for N=1, F=0, FT1=0, FT0=1) or Display lines 2, Char Font 5x8, font table 1 (European)
    command(c.DISPLAYOFF)
    command(c.ENTRY) # Set entry mode to direction right, no shift
    command(c.POWERON|c.GRAPHIC) # Turn internal power on and set into graphics mode
    command(c.CLEAR) # Clear Display
    sleep(1e-3*1.5)
    command(c.DISPLAYON)


testImage1 = bytearray(b'\x08\xf8\xf8\x08\x18\x00\xe0\xf0Pp`\x00 pp\xd0\xd0\x80\x10\xfc\xfc\x10\x90\x80\x00\x00\x00\x00\x00\x00\x08\xf8\xf8\x08\x00\x10\xf00\xf00\xe0\x00\xa0\xf0P\xf0\xe0\x00\xe0\xf0\x10\xe0\xf0\x10\xe0\xf0Pp`\x00\x00\x00\x00\x00\x00\x08x\xc0\xf8\xc0x\x08\xb08h\xe8\xd8\x00\xf8\xfc\x04\xfc\xf8\x00\xf8\xfc\x04\xfc\xf8\x00\x08\x08\xfc\xfc\x00\x00\xf8\xfc\x04\xfc\x01\x01\x01\xe1\xa0\xa0\xa0\xa1\xa1\xa1\xa1\xa0\xa1\xa1\xa1\xa1\xa1\xa0\xa0\xa0\xa1\xa1\xa1\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa1\xa1\xa1\xa1\xa0\xa0\xa1\xa0\xa1\xa0\xa1\xa0\xa1\xa1\xa1\xa1\xa1\xa1\xa4\xa5\xa5\xa7\xa3\xa0\xa0\xa1\xa1\xa1\xa1\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa1\xa0\xa1\xa0\xa0\xa1\xa1\xa1\xa1\xa0\xa0\xa0\xa1\xa1\xa1\xa0\xa0\xa0\xa1\xa1\xa1\xa0\xa0\xa1\xa1\xa1\xa1\xa1\xa1\xa0\xe1\x01\x01')
testImage2 = bytearray([0xFF]*200)

def _display(img):
    _reset()
    command(c.DDRAMADDR,c.CGRAMADDR)
    data(list(img[0:len(img)/2]))
    command(c.DDRAMADDR,c.CGRAMADDR|0x01)
    data(list(img[len(img)/2:]))

if __name__ == '__main__':
    sleep(.5)
    _reset()
    c = ws0010

    print ('Hit Enter')
    raw_input()
    _display(testImage1)
    print ('Hit Enter')
    raw_input()
    _display(testImage2)
    print ('Hit Enter')
    raw_input()
    _display(testImage1)
    raw_input()

    command(0x01)
