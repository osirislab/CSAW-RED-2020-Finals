from gmpy2 import divm, mpz, mul, powmod
import sys

import SECRET

#key material
n = 104525132490556452593202847360958867443850727021139374664119771884926217842051539965479047872905144890766357397753662519890618428457072902974515214064289896674717388849969373481670774897894594962128470900125169816586277785525675183392237296768481956391496477386266086799764706674035243519651786099303959008271
e = 65537
d = SECRET.d

def sign(data):
	return pow(int(data.hex(), 16), d, n)

def verify(data, sig):
	return int(data.hex(), 16) == pow(int(sig.hex(), 16), e, n)

def main():
	print("Spellcasting as a Service - SaaS")
	print("Unlimited spell slots with a 3-year subscription!\n")

	print("Sign your spell and then cast it\n")

	print("sign <spell>")
	print("cast <signature> <spell>")
	print("\\\\")

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
					print("You cast your spell! It does nothing :(")
			elif parts[0] in ["quit", "exit"]:
				print("Vanishing!")
				return
			else:
				raise Exception()
		except:
			print("Incorrect amount of magic focus...")
			print("...try again?")

if __name__ == "__main__":
	test_str = b"this is not the string you're looking for"
	if not verify(test_str, bytes.fromhex(hex(sign(test_str))[2:])):
		raise Exception()
	main()
