#!/usr/bin/python
# coding: UTF-8
from time import sleep
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pins_db = [ 25, 24, 23, 27]
RS = 7
E = 8
for pin in pins_db:
   GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

GPIO.setup(E, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(RS, GPIO.OUT, initial=GPIO.LOW)


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


def command(self, *cmd):
    """
    Sends a command or sequence of commands through the bus

    :param cmd: A spread of commands.
    :type cmd: int
    """
    self._write_bytes(list(cmd), self._cmd_mode)

def data(self, data):
    """
    Sends a data byte or sequence of data bytes through to the bus.
    If the bus is in four bit mode, each byte is sent as two 4 bit values.

    :param data: A data sequence.
    :type data: list, bytearray
    """
    self._write_bytes(data, self._data_mode)

def _write_bytes(self, data, mode):
    gpio = self._gpio
    gpio.output(self._RS, self.mode)
    gpio.output(self._E, gpio.LOW)  # Active low
    for byte in data:
        if self.mode:
            _write(byte, 8)
        else:
            _write(byte>>4, 4)
            _write(byte, 4)
        if mode == self._cmd_mode:
            sleep(1e-6*40)
        else:
            sleep(1e-6)


def _write(self, value, bits):
    assert bits in (4,8)
    gpio = self._gpio
    gpio.output(self._E, gpio.LOW)
    for i in range(bits):
        gpio.output(self.PINS[i], (value >> i) & 0x01)
    gpio.output(self._E, gpio.HIGH)
    sleep(1e-6*0.5) # Minimum time for enable is ~1/2 uS
    gpio.output(self._E, gpio.LOW)


def _reset():
    c = ws0010
    mode = c.DL4
    command(0x00, 0x00, c.FUNCTIONSET|mode) # Sends five 0s and set data length

    command(c.DISPLAYOFF)
    command(c.ENTRY) # Set entry mode to direction right, no shift
    command(c.POWERON|c.GRAPHIC) # Turn internal power on and set into graphics mode
    command(c.CLEAR) # Clear Display
    sleep(1e-3*1.5)
    command(c.DISPLAYON)


testImage = bytearray(b'\x08\xf8\xf8\x08\x18\x00\xe0\xf0Pp`\x00 pp\xd0\xd0\x80\x10\xfc\xfc\x10\x90\x80\x00\x00\x00\x00\x00\x00\x08\xf8\xf8\x08\x00\x10\xf00\xf00\xe0\x00\xa0\xf0P\xf0\xe0\x00\xe0\xf0\x10\xe0\xf0\x10\xe0\xf0Pp`\x00\x00\x00\x00\x00\x00\x08x\xc0\xf8\xc0x\x08\xb08h\xe8\xd8\x00\xf8\xfc\x04\xfc\xf8\x00\xf8\xfc\x04\xfc\xf8\x00\x08\x08\xfc\xfc\x00\x00\xf8\xfc\x04\xfc\x01\x01\x01\xe1\xa0\xa0\xa0\xa1\xa1\xa1\xa1\xa0\xa1\xa1\xa1\xa1\xa1\xa0\xa0\xa0\xa1\xa1\xa1\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa1\xa1\xa1\xa1\xa0\xa0\xa1\xa0\xa1\xa0\xa1\xa0\xa1\xa1\xa1\xa1\xa1\xa1\xa4\xa5\xa5\xa7\xa3\xa0\xa0\xa1\xa1\xa1\xa1\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa1\xa0\xa1\xa0\xa0\xa1\xa1\xa1\xa1\xa0\xa0\xa0\xa1\xa1\xa1\xa0\xa0\xa0\xa1\xa1\xa1\xa0\xa0\xa1\xa1\xa1\xa1\xa1\xa1\xa0\xe1\x01\x01')


if __name__ == '__main__':
    sleep(.5)
    _reset()

    command(c.DDRAMADDR,c.CGRAMADDR)
    data(testImage[0:len(testImage)/2])

    command(c.DDRAMADDR,c.CGRAMADDR|0x01)
    data(testImage[len(testImage)/2:])

    sleep(5)

    command(0x01)
