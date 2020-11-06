message = "flag{dont_eat_deadfish}"
'''
i +1
d -1
s ** s
d output
'''
a = 0
for char in message:
	value = ord(char)
	while a != value:
		if a ** 2 <= value and a > 1:
			a = a ** 2
			print("s", end="")
		elif a < value:
			a += 1
			print("i", end="")
		elif a > value:
			a -= 1
			print("d", end="")
	print("o")

