print ''
print "   ",
for i in range(0,16):
    print "{:3d}  ".format(i),
print ''

for i in range(0,16):
    print "{:3d}  ".format(i*16),
    for j in range(0,16):
        if (j*16)+i > 32:
            print "{0}    ".format(unichr((j*16)+i).encode('utf-8')),
        else:
            print "     ",
    print ''
