#!/bin/env python3

'''
Deadfish Interpreter written in python3.
Written by chill0r.
Everything is free to use - no restrictions.

Startup arguments:
	-strict: Output errors (and abort) on invalid characters and Overflow
	-p program: Execute program (does not exit if not told so)
	
Accepted characters (case sensitive!):
	i / x: increment by 1
	d: decrement by 1
	s / k: square
	o / c: print accumulator
	h: exit interpreter (and stop program) (non standard)
	r: reset accumulator to 0 (non standard)
'''
import sys

class DeadfishError(Exception):	
	def __init__(self, message):
		print(message)
		sys.exit(1)

prog = sys.argv[sys.argv.index('-p')+1] if '-p' in sys.argv else None
strict = '-strict' in sys.argv

acc = 0
i = 0

print('''Python3 Deadfish interpreter version 0.1''')

while True:
	if not bool(prog):
		prog = input('>>')
	for char in prog:
		if strict and not char in ['i', 'x', 'd', 's', 'k', 'h', 'o', 'c', 'r']:
			raise DeadfishError('Invalid character {} at index {}'.format(char, i))
		if char in ['i','x']:
			acc += 1
		elif char == 'd':
			acc -= 1
		elif char in ['s', 'k']:
			acc *= acc
		elif char == 'h':
			print('Long live the fish!')
			sys.exit(0)
		elif char == 'r':
			acc = 0
		if acc < 0 or acc == 256:
			if strict:
				raise DeadfishError('Overflow at char {} (Index {}) accumulator = {}'.format(char, i, acc))
			else:
				acc = 0
		if char in ['o', 'c']:
			print(chr(acc), end="")
		i += 1
	prog = None
	i = 0