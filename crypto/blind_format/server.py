from gmpy2 import divm, mpz, mul, powmod
import sys

import SECRET

#key material
n = 151344532527925556350974757629285375760854276898058546405594026203997410437714722120318262940225090378982962568087555459772015725247304252516252133233201141501772358742227659485723099848701870054530883080763906512752831582408291010602491760336942824607523416310244169661388738172980663338461180475498980566447
e = 65537
d = SECRET.d

def sign(data):
	return pow(int(data.hex(), 16), d, n)

def verify(data, sig):
	return int(data.hex(), 16) == pow(int(sig.hex(), 16), e, n)

def main():
	print("Hex Casting as a Service - HCaaS")
	print("Unlimited spell slots with a 3-year subscription!\n")

	print("Sign your spell and then cast it\n")

	print("sign <spell>")
	print("cast <signature> <spell>\\\\")

	while True:
		parts = sys.stdin.readline()[:-1].split(" ")

		try:
			if parts[0] == "sign":
				spell = bytes.fromhex(parts[1])

				if spell.find(b"hocus pocus") != -1:
					raise Exception()

				print("{}".format(hex(sign(spell))[2:]))
			elif parts[0] == "cast":
				sig = bytes.fromhex(parts[1])
				spell = bytes.fromhex(parts[2])

				if not verify(spell, sig):
					raise Exception()

				if spell == b"hocus pocus":
					print("Something just appeared out of nowhere!")
					with open("flag") as file:
						print("".join(file.readlines()))
				else:
					print("You cast your spell! It does nothing. :(")
			elif parts[0] in ["quit", "exit"]:
				print("Vanishing!")
				return
			else:
				raise Exception()
		except:
			raise
			print("Incorrect amount of magic focus...")
			print("...try again?")

if __name__ == "__main__":
	test_str = b"thstrhtrh"
	if not verify(test_str, bytes.fromhex(hex(sign(test_str))[2:])):
		raise Exception()
	main()
