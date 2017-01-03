# coding: UTF-8

from __future__ import unicode_literals


def fntlines(start, end, w,h):
	for i in range (start,end+1):
		x = (i % 16)*w
		y = i/16*h
		print "char id={0} x={1} y={2} width={3} height={4} xoffset=0 yoffset=0 xadvance={5} page=0 chnl=0".format(i,x,y,w,h,w)
