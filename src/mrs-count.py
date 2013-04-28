import os

file = open('ace.mrs.out')
lines = file.readlines()
file.close()

i = 0
r = 0
for line in lines:
    if 'SENT:' in line:
        i += 1
    if 'SKIP:' in line:
        r += 1
        
print i
print r

