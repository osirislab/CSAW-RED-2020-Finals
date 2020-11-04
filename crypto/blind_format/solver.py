from gmpy2 import divm, mpz, mul, powmod
from pwn import remote
import sys
import time

host = "127.0.0.1"
port = 8779

server = remote(host, port)

#key material
n = 151344532527925556350974757629285375760854276898058546405594026203997410437714722120318262940225090378982962568087555459772015725247304252516252133233201141501772358742227659485723099848701870054530883080763906512752831582408291010602491760336942824607523416310244169661388738172980663338461180475498980566447
e = 65537

def encrypt(data):
	return pow(int(data.hex(), 16), e, n)

def try_sign(spell):
	print("sign " + spell.hex() + "\n")
	server.send("sign " + spell.hex() + "\n")

	line = server.recvuntil("\n").decode("utf-8")
	if line.startswith("Incorrect"):
		server.recvuntil("\n")
		return None

	#strip off \r\n
	return line[:-2].encode("utf-8")

def try_cast(spell, sig):
	server.send(" ".join(["cast", sig.hex(), spell.hex()]) + "\n")

	line = server.recvuntil("\n").decode("utf-8")
	print(line)
	if line.startswith("Incorrect"):
		server.recvuntil("\n")
		return False
	elif line.startswith("You"):
		return True

	#strip off \r\n
	return server.recvuntil("\n")[:-2]

class UE(BaseException):
	def __init__(self):
		pass

def main():
	spell = b"hocus pocus"

	c = encrypt(spell)
	c = int(spell.hex(), 16)
	r = 1
	d = 0
	sig_c_prime = None 

	while sig_c_prime is None:
		if not r % 100:
			print(r, d)
			print(sig_c_prime)

		try:
			c_prime = mul(c, powmod(r, e, n)) % n
			print(0, hex(c_prime)[2:])
			msg = bytes.fromhex(("0" if len(hex(c_prime)) % 2 else "") + hex(c_prime)[2:])
			#print(1, msg)

			if any([x in [ord("\0"), ord(" "), ord("\t"), ord("\r"), ord("\n")] for x in msg]):
				raise UE()
			resp = try_sign(msg)
			#print(2, resp)

			if resp is not None:
				sig_c_prime = int(resp, 16)
				break
		except KeyboardInterrupt:
			raise
		except UE:
			d += 1
		r += 1

	sig = hex( divm(sig_c_prime, r, n) )[2:]
	print(bytes.fromhex(sig))
	flag = try_cast(spell, bytes.fromhex(sig)).decode("utf-8")
	print("flag:", flag)

if __name__ == "__main__":
	print(server.recvuntil("\\\\\r\n"))
	try_str = b'hocus  pocus'
	print(try_sign(try_str))
	print(try_sign(try_str).decode("utf-8"))
	print(try_cast(try_str, bytes.fromhex("0" + try_sign(try_str).decode("utf-8"))))
	main()
