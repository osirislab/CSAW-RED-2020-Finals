from gmpy2 import divm, mpz, mul, powmod
import hashlib
import sys

import SECRET

#key material
n = 151344532527925556350974757629285375760854276898058546405594026203997410437714722120318262940225090378982962568087555459772015725247304252516252133233201141501772358742227659485723099848701870054530883080763906512752831582408291010602491760336942824607523416310244169661388738172980663338461180475498980566447
e = 65537
d = SECRET.d

def hash(str):
	temp = hashlib.sha256()
	temp.update(str.encode("utf-8"))
	return temp.hexdigest()

def sign(data):
	return hex( pow(int(data, 16), d, n) )[2:]

def verify(data, sig):
	return int(data, 16) == pow(int(sig, 16), e, n)

def main():
	parts = sys.stdin.readline()[:-1].split(" ")

	try:
		if parts[0] == "sign":
			fmt = " ".join(parts[1:])

			if fmt.find("%") != -1 or fmt.find("hocus pocus") != -1:
				raise Exception()

			print("{}".format(sign(hash(fmt))), end = "")
		elif parts[0] == "verify":
			sig = parts[1]
			fmt = " ".join(parts[2:])

			if not verify(hash(fmt), sig):
				raise Exception()

			print("{}".format(fmt))
		else:
			raise Exception()
	except:
		print("%s", end = "")

if __name__ == "__main__":
	main()
